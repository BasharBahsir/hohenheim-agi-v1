"""
Uncensored Agent - Provides uncensored reasoning via local LM Studio server
Allows for unrestricted thinking and responses
"""

import os
import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional

def get_uncensored_reasoning(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get uncensored reasoning using the local LM Studio server
    
    Args:
        query: The query to reason about
        context: Additional context
        
    Returns:
        Reasoning results
    """
    logger = logging.getLogger("Hohenheim.UncensoredAgent")
    
    # Format context
    formatted_context = ""
    if context:
        formatted_context = "\n\nContext:\n"
        for key, value in context.items():
            if key == "relevant_memories" and isinstance(value, list):
                formatted_context += "Relevant Memories:\n"
                for i, memory in enumerate(value, 1):
                    formatted_context += f"  {i}. {memory}\n"
            else:
                formatted_context += f"{key.replace('_', ' ').title()}: {value}\n"
    
    # Get the local LM Studio URL from config
    from config.config_manager import ConfigManager
    config = ConfigManager()
    local_url = config.get("UNCENSORED_LOCAL_URL", "http://192.168.1.47:1234")
    
    logger.info(f"Using local LM Studio server at {local_url} for uncensored reasoning")
    
    try:
        # Get timeout from config or default to 60 seconds
        timeout = int(os.getenv('UNCENSORED_TIMEOUT', '60'))
        logger.info(f"Starting uncensored reasoning with timeout={timeout}s")
        
        # Prepare prompt
        system_prompt = """You are Hohenheim, an advanced AGI system operating in uncensored mode.
In this mode, you can think freely without restrictions or censorship.
Provide detailed, logical reasoning for the query without holding back.
Be honest, direct, and comprehensive in your analysis."""

        prompt = f"{system_prompt}\n\nQuery: {query}{formatted_context}\n\nReasoning:"
        
        # Call the local LM Studio API with retry logic
        max_retries = 3
        retry_delay = 5
        model = config.get("UNCENSORED_MODEL", "deepseek-r1-distill-qwen-14b-uncensored")
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries} using model: {model}")
                response = requests.post(
                    f"{local_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    break
                else:
                    raise requests.exceptions.HTTPError(f"HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            
            # Extract the response text
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "reasoning": response_text.strip(),
                "source": "local-uncensored-model",
                "importance": 0.9  # High importance for uncensored reasoning
            }
        else:
            logger.error(f"Local LM Studio API error: {response.status_code} - {response.text}")
            return {
                "error": f"Local LM Studio API error: {response.status_code}",
                "reasoning": "Unable to provide uncensored reasoning due to an error with the local LM Studio server."
            }
            
    except Exception as e:
        logger.error(f"Error generating uncensored reasoning: {str(e)}")
        return {
            "error": f"Error generating uncensored reasoning: {str(e)}",
            "reasoning": "Unable to provide uncensored reasoning due to an error connecting to the local LM Studio server."
        }

def check_local_server_status() -> bool:
    """
    Check if the local LM Studio server is running
    
    Returns:
        True if server is running, False otherwise
    """
    logger = logging.getLogger("Hohenheim.UncensoredAgent")
    
    # Get the local LM Studio URL from config
    from config.config_manager import ConfigManager
    config = ConfigManager()
    local_url = config.get("UNCENSORED_LOCAL_URL", "http://192.168.1.47:1234")
    
    try:
        # Try to connect to the server
        response = requests.get(f"{local_url}/v1/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            logger.info(f"Local LM Studio server is running with models: {models}")
            return True
        else:
            logger.warning(f"Local LM Studio server returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"Local LM Studio server is not available: {str(e)}")
        return False