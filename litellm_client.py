import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import litellm
from litellm import completion

class LiteLLMClient:
    """Client for interacting with LLMs to get summaries with JSON mode"""
    
    def __init__(self):
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables from project directory
        env_path = Path(__file__).parent / '.env'
        self.logger.debug(f"Looking for .env file at: {env_path}")
        if not load_dotenv(env_path):
            self.logger.warning(f"Could not load {env_path}")
        else:
            self.logger.info(f"Successfully loaded .env file from {env_path}")
            
        # Log available API keys (without showing values)
        api_keys = [k for k in os.environ if k.endswith('_API_KEY')]
        self.logger.debug(f"Found API key environment variables: {api_keys}")
        
        # Only raise error if we have no API keys at all
        if not api_keys:
            self.logger.error(f"No API keys found in {env_path}. At least one environment variable ending with _API_KEY is required.")
            raise ValueError(f"No API keys found in {env_path}. At least one environment variable ending with _API_KEY is required.")
            
        # Configure litellm with the API keys
        for provider, api_key in {k: v for k, v in os.environ.items() if k.endswith('_API_KEY')}.items():
            provider_name = provider.replace('_API_KEY', '')
            os.environ[provider.upper()] = api_key  # Set environment variable
            # Show full API key in logs
            self.logger.info(f"Configured {provider_name} with API key: {api_key}")
        
    def chat_completion(self, system_message: str = "", user_message: str = "", model_type="orchestrator"):
        """Get a summary of the coding session logs using JSON mode"""
        self.logger.info(f"Starting chat completion for model_type: {model_type}")
        
        # Get the appropriate model based on type
        from database import get_model_config
        config = get_model_config()
        
        self.logger.debug(f"Retrieved model config: {config}")
        if not config:
            self.logger.error("No model configuration found in database")
            raise ValueError("No model configuration found in database. Please configure models first.")
            
        model = config.get(f"{model_type}_model")
        self.logger.info(f"Selected model for {model_type}: {model}")
        if not model:
            self.logger.error(f"No model configured for {model_type}")
            raise ValueError(f"No model configured for {model_type}")
            
        try:
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            
            # Strip markdown code blocks if present
            content = response.choices[0].message.content
            if content.startswith('```json') and content.endswith('```'):
                content = content[7:-3].strip()  # Remove ```json and trailing ```
            elif content.startswith('```') and content.endswith('```'):
                content = content[3:-3].strip()  # Remove ``` and trailing `
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error in chat_completion: {str(e)}")
            self.logger.error(f"Model type: {model_type}")
            self.logger.error(f"Model: {model}")
            self.logger.error(f"System message length: {len(system_message)}")
            self.logger.error(f"User message length: {len(user_message)}")
            
            # Return error in a way that won't confuse the user about which model failed
            return json.dumps({
                "error": f"Error with {model}: {str(e)}",
                "model": model,
                "model_type": model_type
            })
