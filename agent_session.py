import os, json, traceback, subprocess, sys, uuid
import threading
import datetime
import queue
import io
import logging
from pathlib import Path
import time
import re

def normalize_path(path_str):
    """Normalize a path string to absolute path with forward slashes."""
    if not path_str:
        return None
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(path_str).resolve()
        # Convert to string with forward slashes
        normalized = str(path).replace('\\', '/')
        # Log both the input and output paths
        logging.debug(f"Path normalization: {path_str} -> {normalized}")
        return normalized
    except Exception as e:
        logging.error(f"Error normalizing path {path_str}: {e}")
        return None

class AgentSession:
    def __init__(self, workspace_path, task, config=None):
        self.workspace_path = normalize_path(workspace_path)
        self.task = task
        self.output_buffer = io.StringIO()
        self.process = None
        self._stop_event = threading.Event()
        self.session_id = str(uuid.uuid4())[:8]  # For logging
        self._buffer_lock = threading.Lock()  # Add lock for thread-safe buffer access
        
        # Load configuration with defaults
        default_config = {
            'stability_duration': 10,
            'output_buffer_max_length': 10000
        }
        self.config = {**default_config, **(config or {})}
        
        logging.info(f"[Session {self.session_id}] Initialized with workspace: {self.workspace_path}")
        logging.info(f"[Session {self.session_id}] Configuration: {self.config}")

    def start(self) -> bool:
        """
        Start the aider session.
        
        Returns:
            bool: True if session started successfully, False otherwise
        """
        try:
            logging.info(f"[Session {self.session_id}] Starting aider session in workspace: {self.workspace_path}")
            
            # Create startupinfo to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Start aider process with unbuffered output
            cmd = f'aider --map-tokens 1024 --no-show-model-warnings --model openrouter/google/gemini-flash-1.5 --message "{self.task}"'
            logging.info(f"[Session {self.session_id}] Executing command: {cmd}")
            
            # Set up environment with forced unbuffering
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(Path(self.workspace_path).resolve()),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                env=env
            )
            
            logging.info(f"[Session {self.session_id}] Process started with PID: {self.process.pid}")
            logging.info(f"[Session {self.session_id}] Working directory: {self.workspace_path}")

            # Start output reading threads
            stdout_thread = threading.Thread(
                target=self._read_output, 
                args=(self.process.stdout, "stdout"), 
                daemon=True,
                name=f"stdout-{self.session_id}"
            )
            stderr_thread = threading.Thread(
                target=self._read_output, 
                args=(self.process.stderr, "stderr"), 
                daemon=True,
                name=f"stderr-{self.session_id}"
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            logging.info(f"[Session {self.session_id}] Started output processing threads")

            # Verify threads are running
            for thread in [stdout_thread, stderr_thread]:
                if not thread.is_alive():
                    logging.error(f"[Session {self.session_id}] Thread {thread.name} failed to start")
                    return False
                logging.info(f"[Session {self.session_id}] Thread {thread.name} is running")

            return True
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Failed to start aider session: {e}", exc_info=True)
            return False

    def _read_output(self, pipe, pipe_name):
        """Read output from a pipe and write directly to buffer"""
        try:
            logging.info(f"[Session {self.session_id}] Started reading from {pipe_name}")
            for line in iter(pipe.readline, ''):
                if self._stop_event.is_set():
                    break
                    
                logging.debug(f"[Session {self.session_id}] {pipe_name} received: {line.strip()}")
                
                # Immediately write to buffer with lock
                with self._buffer_lock:
                    self.output_buffer.seek(0, 2)  # Seek to end
                    self.output_buffer.write(line)
                    logging.debug(f"[Session {self.session_id}] Added to buffer: {line.strip()}")
                    
                # Flush the pipe to ensure we get output immediately
                pipe.flush()
                
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error reading from {pipe_name}: {e}", exc_info=True)
        finally:
            try:
                pipe.close()
                logging.info(f"[Session {self.session_id}] Closed {pipe_name} pipe")
            except Exception as e:
                logging.error(f"[Session {self.session_id}] Error closing {pipe_name} pipe: {e}", exc_info=True)

    def get_output(self):
        """Get the current output buffer contents"""
        try:
            # Save current position
            pos = self.output_buffer.tell()
            # Go to beginning
            self.output_buffer.seek(0)
            # Read all content
            output = self.output_buffer.read()
            # Restore position
            self.output_buffer.seek(pos)
            
            return output
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error getting output: {e}", exc_info=True)
    def _echo_message(self, message: str) -> None:
        """
        Echo the sent message to the output buffer, simulating user input in the CLI.

        Args:
            message (str): The message to echo
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            echo_line = f"<span class='user-message'>[{timestamp}] USER: {message}</span>\n"
            
            with threading.Lock():
                self.output_buffer.seek(0, 2)  # Seek to end
                self.output_buffer.write(echo_line)
                
            logging.debug(f"[Session {self.session_id}] Echoed message to output buffer: {message}")
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error echoing message: {e}", exc_info=True)

    def is_ready(self) -> bool:
        """
        Check if the process is ready by verifying no changes in stdout for configured duration.
        
        Returns:
            bool: Indicating if the process is stable and ready
        """
        try:
            # Use configured stability duration
            stability_duration = self.config['stability_duration']
            
            # Initial output snapshot
            initial_output = self.get_output()
            logging.debug(f"[Session {self.session_id}] Initial output length: {len(initial_output)}")
            
            # Track time and output stability
            start_time = time.time()
            while time.time() - start_time < stability_duration:
                # Short sleep to prevent tight looping
                time.sleep(1)
                
                # Get current output
                current_output = self.get_output()
                logging.debug(f"[Session {self.session_id}] Current output length: {len(current_output)}")
                
                # Check if output has changed
                if current_output != initial_output:
                    logging.debug(f"[Session {self.session_id}] Output changed during stability check")
                    return False
            
            # No changes detected for entire duration
            logging.info(f"[Session {self.session_id}] Process stable for {stability_duration} seconds")
            
            return True
        
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error in readiness check: {e}", exc_info=True)
            return False

    def send_message(self, message: str, timeout: int = 10) -> bool:
        """
        Send a message to the aider process.
        
        Args:
            message (str): The message to send to the aider process
            timeout (int, optional): Timeout for sending the message. Defaults to 10 seconds.
        
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            if not self.process or self.process.poll() is not None:
                logging.error(f"[Session {self.session_id}] Cannot send message: Process is not running")
                return False
            
            # Sanitize and prepare message
            self._echo_message(message)  # Echo message to output before sending
            
            sanitized_message = message.replace('"', '\\"')
            logging.info(f"[Session {self.session_id}] Sending message to Aider: {sanitized_message}")
            
            # Send message via stdin
            try:
                self.process.stdin.write(sanitized_message + "\n")
                self.process.stdin.flush()
                logging.debug(f"[Session {self.session_id}] Message sent to Aider successfully")
                return True
            except (BrokenPipeError, IOError) as pipe_error:
                logging.error(f"[Session {self.session_id}] Pipe error sending message: {pipe_error}")
                return False
        
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error sending message: {e}", exc_info=True)
            return False

    def cleanup(self) -> None:
        """Clean up the aider session"""
        try:
            logging.info(f"[Session {self.session_id}] Starting cleanup")
            self._stop_event.set()
            if self.process:
                logging.info(f"[Session {self.session_id}] Terminating process {self.process.pid}")
                
                # Close stdin to prevent further writes
                try:
                    if self.process.stdin:
                        self.process.stdin.close()
                except Exception as stdin_close_error:
                    logging.warning(f"[Session {self.session_id}] Error closing stdin: {stdin_close_error}")
                
                # Terminate process
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                    logging.info(f"[Session {self.session_id}] Process terminated successfully")
                except subprocess.TimeoutExpired:
                    logging.warning(f"[Session {self.session_id}] Process did not terminate, forcing kill")
                    self.process.kill()
                
                # Close stdout and stderr
                try:
                    if self.process.stdout:
                        self.process.stdout.close()
                    if self.process.stderr:
                        self.process.stderr.close()
                except Exception as pipe_close_error:
                    logging.warning(f"[Session {self.session_id}] Error closing pipes: {pipe_close_error}")
            
            logging.info(f"[Session {self.session_id}] Cleanup completed")
        except Exception as e:
            logging.error(f"[Session {self.session_id}] Error during cleanup: {e}", exc_info=True)
