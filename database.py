import sqlite3
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

DATABASE_PATH = Path("tasks.db")

def init_db():
    """Initialize the SQLite database with required tables."""
    logger.info("Initializing database")
    try:
        # Create database file if it doesn't exist
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initializing database at {DATABASE_PATH}")
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Create model_config table first
            logger.debug("Creating model_config table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    orchestrator_model TEXT NOT NULL DEFAULT 'deepseek/deepseek-chat',
                    aider_model TEXT NOT NULL DEFAULT 'deepseek/deepseek-chat',
                    agent_model TEXT NOT NULL DEFAULT 'deepseek/deepseek-chat',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            logger.debug("model_config table created/verified")
            
            # Insert default model config if not exists
            now = datetime.now().isoformat()
            logger.debug("Inserting default model config...")
            cursor.execute("SELECT COUNT(*) FROM model_config")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("""
                    INSERT INTO model_config (
                        orchestrator_model, aider_model, agent_model, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, ('deepseek/deepseek-chat', 'deepseek/deepseek-chat', 'deepseek/deepseek-chat', now, now))
                logger.info("Inserted default model config")
            else:
                logger.info(f"Model config already exists ({count} rows)")
            
            # Create other tables...
            logger.debug("Creating other tables...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            logger.debug("config table created/verified")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            logger.debug("tasks table created/verified")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    workspace TEXT NOT NULL,
                    repo_path TEXT,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    aider_output TEXT,
                    last_critique TEXT,
                    progress TEXT,
                    thought TEXT,
                    future TEXT,
                    last_action TEXT,
                    progress_history TEXT,
                    thought_history TEXT,
                    pr_url TEXT,
                    error TEXT,
                    completed INTEGER DEFAULT 0,
                    agent_type TEXT DEFAULT 'default'
                )
            """)
            logger.debug("agents table created/verified")
            
            conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def save_agent(agent_id: str, agent_data: Dict) -> bool:
    """Save or update an agent in the database."""
    logger.debug(f"Saving agent {agent_id}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Convert lists to JSON strings
            progress_history = json.dumps(agent_data.get('progress_history', []))
            thought_history = json.dumps(agent_data.get('thought_history', []))
            
            cursor.execute("""
                INSERT OR REPLACE INTO agents (
                    id, workspace, repo_path, task, status, created_at, 
                    last_updated, aider_output, last_critique, progress, 
                    thought, future, last_action, progress_history, 
                    thought_history, pr_url, error, completed, agent_type
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                agent_id,
                agent_data.get('workspace'),
                agent_data.get('repo_path'),
                agent_data.get('task'),
                agent_data.get('status', 'pending'),
                agent_data.get('created_at', datetime.now().isoformat()),
                agent_data.get('last_updated', datetime.now().isoformat()),
                agent_data.get('aider_output', ''),
                agent_data.get('last_critique', ''),
                agent_data.get('progress', ''),
                agent_data.get('thought', ''),
                agent_data.get('future', ''),
                agent_data.get('last_action', ''),
                progress_history,
                thought_history,
                agent_data.get('pr_url', ''),
                agent_data.get('error', ''),
                agent_data.get('completed', 0),
                agent_data.get('agent_type', 'default')
            ))
            conn.commit()
            logger.info(f"Saved agent {agent_id}")
            return True
    except Exception as e:
        logger.error(f"Error saving agent {agent_id}: {e}")
        return False

def get_agent(agent_id: str) -> Optional[Dict]:
    """Get an agent by ID."""
    logger.debug(f"Getting agent {agent_id}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
            row = cursor.fetchone()
            if row:
                agent_data = dict(row)
                # Convert JSON strings back to lists
                agent_data['progress_history'] = json.loads(agent_data['progress_history'])
                agent_data['thought_history'] = json.loads(agent_data['thought_history'])
                logger.info(f"Retrieved agent {agent_id}")
                return agent_data
            logger.info(f"Agent {agent_id} not found")
            return None
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        return None

def get_all_agents() -> Dict[str, Dict]:
    """Get all agents."""
    logger.debug("Getting all agents...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents")
            rows = cursor.fetchall()
            agents = {}
            for row in rows:
                agent_data = dict(row)
                # Convert JSON strings back to lists
                agent_data['progress_history'] = json.loads(agent_data['progress_history'])
                agent_data['thought_history'] = json.loads(agent_data['thought_history'])
                agents[agent_data['id']] = agent_data
            logger.info("Retrieved all agents")
            return agents
    except Exception as e:
        logger.error(f"Error getting all agents: {e}")
        return {}

def delete_agent(agent_id: str) -> bool:
    """Delete an agent from the database."""
    logger.debug(f"Deleting agent {agent_id}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
            conn.commit()
            logger.info(f"Deleted agent {agent_id}")
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {e}")
        return False

def save_task(task_data: Dict) -> int:
    """Save a task to the database."""
    logger.debug(f"Saving task {task_data.get('title')}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, description, created_at)
                VALUES (:title, :description, :created_at)
            """, {
                'title': task_data.get('title'),
                'description': task_data.get('description'),
                'created_at': datetime.now().isoformat()
            })
            conn.commit()
            logger.info(f"Saved task {task_data.get('title')}")
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error saving task {task_data.get('title')}: {e}")
        return -1

def get_all_tasks() -> List[Dict]:
    """Get all tasks."""
    logger.debug("Getting all tasks...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks")
            tasks = [dict(row) for row in cursor.fetchall()]
            logger.info("Retrieved all tasks")
            return tasks
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        return []

def get_config(key: str) -> Optional[str]:
    """Get a config value."""
    logger.debug(f"Getting config {key}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            result = cursor.fetchone()
            value = result[0] if result else None
            logger.info(f"Retrieved config {key}: {value}")
            return value
    except Exception as e:
        logger.error(f"Error getting config {key}: {e}")
        return None

def save_config(key: str, value: str) -> bool:
    """Save a config value."""
    logger.debug(f"Saving config {key}...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO config (key, value)
                VALUES (?, ?)
            """, (key, value))
            conn.commit()
            logger.info(f"Saved config {key}: {value}")
            return True
    except Exception as e:
        logger.error(f"Error saving config {key}: {e}")
        return False

def get_model_config() -> Optional[Dict]:
    """Get the current model configuration."""
    logger.debug("Getting model config...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM model_config ORDER BY id DESC LIMIT 1")
            config = cursor.fetchone()
            if config:
                result = dict(config)
                logger.info(f"Retrieved model config: {result}")
                return result
            else:
                logger.warning("No model config found in database")
                return None
    except Exception as e:
        logger.error(f"Error getting model config: {e}")
        return None

def set_model_config(orchestrator_model: str, aider_model: str, agent_model: str) -> bool:
    """Set the model configuration."""
    logger.debug("Setting model config...")
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_config (
                    orchestrator_model, aider_model, agent_model,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                orchestrator_model,
                aider_model,
                agent_model,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()
            logger.info("Set model config")
            return True
    except Exception as e:
        logger.error(f"Error setting model config: {e}")
        return False

# Initialize the database when this module is imported
init_db()
