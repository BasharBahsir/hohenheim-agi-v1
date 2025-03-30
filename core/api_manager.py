"""
API Manager - Handles all external API integrations
Primarily manages DeepSeek-Chat and Claude-3.7-Sonnet APIs for reasoning capabilities
"""

import os
import requests
import json
import logging
from typing import Dict, List, Any, Optional

class APIManager:
    """
    Manages all external API connections for the Hohenheim AGI system.
    Handles authentication, rate limiting, and response processing.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the API Manager with configuration
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger("Hohenheim.APIManager")
        
        # Load API keys from config
        self.deepseek_api_key = self.config.get("DEEPSEEK_API_KEY")
        self.claude_api_key = self.config.get("CLAUDE_API_KEY")
        
        # Load model configurations
        self.deepseek_model = self.config.get("DEEPSEEK_MODEL", "deepseek-chat")
        self.deepseek_max_tokens = int(self.config.get("DEEPSEEK_MAX_TOKENS", 4096))
        self.deepseek_temperature = float(self.config.get("DEEPSEEK_TEMPERATURE", 0.7))
        
        self.claude_model = self.config.get("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
        self.claude_max_tokens = int(self.config.get("CLAUDE_MAX_TOKENS", 4096))
        self.claude_temperature = float(self.config.get("CLAUDE_TEMPERATURE", 0.7))
        
        # API endpoints
        self.deepseek_endpoint = "https://api.deepseek.com/v1/chat/completions"
        self.claude_endpoint = "https://api.anthropic.com/v1/messages"
        
        # Verify API keys
        self._verify_api_keys()
        
    def _verify_api_keys(self) -> None:
        """Verify that required API keys are available"""
        if not self.deepseek_api_key and not self.claude_api_key:
            self.logger.warning("No API keys configured. Reasoning capabilities will be limited.")
        elif not self.deepseek_api_key:
            self.logger.warning("DeepSeek API key not configured. Using Claude API only.")
        elif not self.claude_api_key:
            self.logger.warning("Claude API key not configured. Using DeepSeek API only.")
        else:
            self.logger.info("All API keys configured successfully.")
    
    def get_reasoning(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get reasoning results from the configured reasoning API
        
        Args:
            query: The question or problem to reason about
            context: Additional context for reasoning
            
        Returns:
            Reasoning results dictionary
        """
        # By default, use DeepSeek for general reasoning
        if self.deepseek_api_key:
            return self._call_deepseek_api(query, context)
        elif self.claude_api_key:
            return self._call_claude_api(query, context)
        else:
            self.logger.error("No reasoning APIs available")
            return {
                "error": "No reasoning APIs configured",
                "reasoning": "Unable to process reasoning request due to missing API configuration."
            }
    
    def get_advanced_reasoning(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get advanced reasoning results for complex tasks (code generation, analysis)
        
        Args:
            query: The question or problem to reason about
            context: Additional context for reasoning
            
        Returns:
            Reasoning results dictionary
        """
        # Use Claude for advanced reasoning (code generation, analysis)
        if self.claude_api_key:
            return self._call_claude_api(query, context)
        elif self.deepseek_api_key:
            return self._call_deepseek_api(query, context)
        else:
            self.logger.error("No reasoning APIs available")
            return {
                "error": "No reasoning APIs configured",
                "reasoning": "Unable to process reasoning request due to missing API configuration."
            }
    
    def _call_deepseek_api(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call the DeepSeek API for reasoning
        
        Args:
            query: The query to reason about
            context: Additional context
            
        Returns:
            Reasoning results
        """
        self.logger.info(f"Using {self.deepseek_model} for reasoning")
        
        # Prepare context for the API
        formatted_context = self._format_context_for_deepseek(context)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            payload = {
                "model": self.deepseek_model,
                "messages": [
                    {"role": "system", "content": "You are Hohenheim, an advanced AGI system. Provide detailed, logical reasoning for the query."},
                    {"role": "user", "content": f"Query: {query}\nContext: {formatted_context}"}
                ],
                "temperature": self.deepseek_temperature,
                "max_tokens": self.deepseek_max_tokens
            }
            
            response = requests.post(
                self.deepseek_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Process and structure the response
                reasoning_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract importance score from reasoning (if available)
                importance = 0.8  # Default high importance for DeepSeek responses
                
                return {
                    "reasoning": reasoning_text,
                    "source": self.deepseek_model,
                    "importance": importance
                }
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                # Fall back to Claude if available
                if self.claude_api_key:
                    self.logger.info("Falling back to Claude API")
                    return self._call_claude_api(query, context)
                return {
                    "error": f"DeepSeek API error: {response.status_code}",
                    "reasoning": "Unable to process reasoning request due to API error."
                }
                
        except Exception as e:
            self.logger.error(f"Error calling DeepSeek API: {str(e)}")
            return {
                "error": f"DeepSeek API exception: {str(e)}",
                "reasoning": "Unable to process reasoning request due to an exception."
            }
    
    def _call_claude_api(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call the Claude API for reasoning
        
        Args:
            query: The query to reason about
            context: Additional context
            
        Returns:
            Reasoning results
        """
        self.logger.info(f"Using {self.claude_model} for reasoning")
        
        # Prepare context for the API
        formatted_context = self._format_context_for_claude(context)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.claude_api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.claude_model,
                "messages": [
                    {"role": "user", "content": f"You are Hohenheim, an advanced AGI system. Provide detailed, logical reasoning for the following query:\n\nQuery: {query}\nContext: {formatted_context}"}
                ],
                "temperature": self.claude_temperature,
                "max_tokens": self.claude_max_tokens
            }
            
            response = requests.post(
                self.claude_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Process and structure the response
                reasoning_text = result.get("content", [{}])[0].get("text", "")
                
                # Extract importance score from reasoning (if available)
                importance = 0.9  # Default importance for Claude responses (higher than DeepSeek)
                
                return {
                    "reasoning": reasoning_text,
                    "source": self.claude_model,
                    "importance": importance
                }
            else:
                self.logger.error(f"Claude API error: {response.status_code} - {response.text}")
                # Fall back to DeepSeek if available
                if self.deepseek_api_key:
                    self.logger.info("Falling back to DeepSeek API")
                    return self._call_deepseek_api(query, context)
                return {
                    "error": f"Claude API error: {response.status_code}",
                    "reasoning": "Unable to process reasoning request due to API error."
                }
                
        except Exception as e:
            self.logger.error(f"Error calling Claude API: {str(e)}")
            return {
                "error": f"Claude API exception: {str(e)}",
                "reasoning": "Unable to process reasoning request due to an exception."
            }
    
    def _format_context_for_deepseek(self, context: Dict[str, Any] = None) -> str:
        """Format context for DeepSeek API"""
        if not context:
            return "No additional context provided."
        
        # Format context as a structured string
        formatted_parts = []
        
        for key, value in context.items():
            if key == "relevant_memories" and isinstance(value, list):
                formatted_parts.append("Relevant Memories:")
                for i, memory in enumerate(value, 1):
                    formatted_parts.append(f"  {i}. {memory}")
            else:
                formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_parts)
    
    def _format_context_for_claude(self, context: Dict[str, Any] = None) -> str:
        """Format context for Claude API"""
        # Similar to DeepSeek formatting but with slight adjustments if needed
        return self._format_context_for_deepseek(context)