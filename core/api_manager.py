"""
API Manager - Handles all external API integrations
Primarily manages DeepSeek-R1 and Sonnet-3.7 APIs for reasoning capabilities
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
        self.sonnet_api_key = self.config.get("SONNET_API_KEY")
        
        # API endpoints
        self.deepseek_endpoint = "https://api.deepseek.com/v1/reasoning"
        self.sonnet_endpoint = "https://api.sonnet.ai/v1/chat/completions"
        
        # Verify API keys
        self._verify_api_keys()
        
    def _verify_api_keys(self) -> None:
        """Verify that required API keys are available"""
        if not self.deepseek_api_key and not self.sonnet_api_key:
            self.logger.warning("No API keys configured. Reasoning capabilities will be limited.")
        elif not self.deepseek_api_key:
            self.logger.warning("DeepSeek API key not configured. Using Sonnet API only.")
        elif not self.sonnet_api_key:
            self.logger.warning("Sonnet API key not configured. Using DeepSeek API only.")
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
        # Determine which API to use based on availability and query complexity
        if self.deepseek_api_key and self._is_complex_reasoning(query):
            return self._call_deepseek_api(query, context)
        elif self.sonnet_api_key:
            return self._call_sonnet_api(query, context)
        elif self.deepseek_api_key:
            return self._call_deepseek_api(query, context)
        else:
            self.logger.error("No reasoning APIs available")
            return {
                "error": "No reasoning APIs configured",
                "reasoning": "Unable to process reasoning request due to missing API configuration."
            }
    
    def _is_complex_reasoning(self, query: str) -> bool:
        """
        Determine if a query requires complex reasoning
        
        Args:
            query: The query to analyze
            
        Returns:
            True if complex reasoning is needed
        """
        # Simple heuristic - can be improved later
        complex_indicators = [
            "why", "how", "explain", "analyze", "compare", "evaluate",
            "synthesize", "design", "develop", "create", "optimize"
        ]
        
        return any(indicator in query.lower() for indicator in complex_indicators)
    
    def _call_deepseek_api(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call the DeepSeek-R1 API for reasoning
        
        Args:
            query: The query to reason about
            context: Additional context
            
        Returns:
            Reasoning results
        """
        self.logger.info("Using DeepSeek-R1 for reasoning")
        
        # Prepare context for the API
        formatted_context = self._format_context_for_deepseek(context)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            payload = {
                "model": "deepseek-r1",
                "messages": [
                    {"role": "system", "content": "You are Hohenheim, an advanced AGI system. Provide detailed, logical reasoning for the query."},
                    {"role": "user", "content": f"Query: {query}\nContext: {formatted_context}"}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
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
                    "source": "deepseek-r1",
                    "importance": importance
                }
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                # Fall back to Sonnet if available
                if self.sonnet_api_key:
                    self.logger.info("Falling back to Sonnet API")
                    return self._call_sonnet_api(query, context)
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
    
    def _call_sonnet_api(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call the Sonnet-3.7 API for reasoning
        
        Args:
            query: The query to reason about
            context: Additional context
            
        Returns:
            Reasoning results
        """
        self.logger.info("Using Sonnet-3.7 for reasoning")
        
        # Prepare context for the API
        formatted_context = self._format_context_for_sonnet(context)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.sonnet_api_key}"
            }
            
            payload = {
                "model": "sonnet-3.7",
                "messages": [
                    {"role": "system", "content": "You are Hohenheim, an advanced AGI system. Provide detailed, logical reasoning for the query."},
                    {"role": "user", "content": f"Query: {query}\nContext: {formatted_context}"}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }
            
            response = requests.post(
                self.sonnet_endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Process and structure the response
                reasoning_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract importance score from reasoning (if available)
                importance = 0.7  # Default importance for Sonnet responses
                
                return {
                    "reasoning": reasoning_text,
                    "source": "sonnet-3.7",
                    "importance": importance
                }
            else:
                self.logger.error(f"Sonnet API error: {response.status_code} - {response.text}")
                # Fall back to DeepSeek if available
                if self.deepseek_api_key:
                    self.logger.info("Falling back to DeepSeek API")
                    return self._call_deepseek_api(query, context)
                return {
                    "error": f"Sonnet API error: {response.status_code}",
                    "reasoning": "Unable to process reasoning request due to API error."
                }
                
        except Exception as e:
            self.logger.error(f"Error calling Sonnet API: {str(e)}")
            return {
                "error": f"Sonnet API exception: {str(e)}",
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
    
    def _format_context_for_sonnet(self, context: Dict[str, Any] = None) -> str:
        """Format context for Sonnet API"""
        # Similar to DeepSeek formatting but with slight adjustments if needed
        return self._format_context_for_deepseek(context)