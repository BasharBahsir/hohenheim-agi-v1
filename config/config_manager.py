"""
Configuration Manager - Handles loading and accessing configuration
Supports .env files, JSON, and YAML configurations
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class ConfigManager:
    """
    Configuration manager for the Hohenheim AGI system.
    Handles loading and accessing configuration from various sources.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.logger = logging.getLogger("Hohenheim.ConfigManager")
        
        # Default configuration
        self.config = {
            # System settings
            "SYSTEM_NAME": "Hohenheim",
            "SYSTEM_VERSION": "0.1.0",
            "SYSTEM_CODENAME": "Neo Jarvis",
            "LOG_LEVEL": "INFO",
            
            # API keys (empty by default, should be loaded from .env)
            "DEEPSEEK_API_KEY": "",
            "SONNET_API_KEY": "",
            
            # Memory settings
            "SHORT_TERM_MEMORY_SIZE": 1000,
            "VECTOR_DB_TYPE": "chroma",  # Options: chroma, faiss, in-memory
            "VECTOR_DB_PATH": "./data/vector_db",
            "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
            
            # Uncensored mode settings
            "QWEN_MODEL_PATH": "./models/qwen-14b",
            
            # Interface settings
            "DEFAULT_INTERFACE": "cli",
            "ENABLE_GUI": False,
            "ENABLE_VOICE": False,
            "CLI_PROMPT": "Hohenheim> "
        }
        
        # Load configuration from various sources
        self._load_env_vars()
        
        if config_path:
            self._load_config_file(config_path)
        else:
            # Try to find config in default locations
            default_locations = [
                "./config.json",
                "./config.yaml",
                "./config.yml",
                "./config/config.json",
                "./config/config.yaml",
                "./config/config.yml"
            ]
            
            for location in default_locations:
                if os.path.exists(location):
                    self._load_config_file(location)
                    break
        
        self.logger.info("Configuration loaded successfully")
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables"""
        # Try to load .env file if dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.logger.info("Loaded configuration from .env file")
        except ImportError:
            self.logger.warning("python-dotenv not installed, skipping .env file loading")
        
        # Override config with environment variables
        for key in self.config.keys():
            env_value = os.environ.get(key)
            if env_value is not None:
                # Convert boolean strings
                if env_value.lower() in ["true", "yes", "1"]:
                    self.config[key] = True
                elif env_value.lower() in ["false", "no", "0"]:
                    self.config[key] = False
                # Convert numeric strings
                elif env_value.isdigit():
                    self.config[key] = int(env_value)
                elif env_value.replace(".", "", 1).isdigit():
                    self.config[key] = float(env_value)
                else:
                    self.config[key] = env_value
    
    def _load_config_file(self, config_path: str) -> None:
        """
        Load configuration from a file
        
        Args:
            config_path: Path to the configuration file
        """
        if not os.path.exists(config_path):
            self.logger.warning(f"Configuration file not found: {config_path}")
            return
        
        try:
            file_ext = os.path.splitext(config_path)[1].lower()
            
            if file_ext in [".json"]:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                self.logger.info(f"Loaded JSON configuration from {config_path}")
                
            elif file_ext in [".yaml", ".yml"]:
                try:
                    import yaml
                    with open(config_path, "r") as f:
                        file_config = yaml.safe_load(f)
                    self.logger.info(f"Loaded YAML configuration from {config_path}")
                except ImportError:
                    self.logger.error("PyYAML not installed, cannot load YAML configuration")
                    return
            else:
                self.logger.warning(f"Unsupported configuration file format: {file_ext}")
                return
            
            # Update configuration with file values
            self.config.update(file_config)
            
        except Exception as e:
            self.logger.error(f"Error loading configuration file {config_path}: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.logger.debug(f"Set configuration {key} = {value}")
    
    def save(self, config_path: str = "./config.json") -> bool:
        """
        Save current configuration to a file
        
        Args:
            config_path: Path to save configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
            
            file_ext = os.path.splitext(config_path)[1].lower()
            
            if file_ext in [".json"]:
                with open(config_path, "w") as f:
                    json.dump(self.config, f, indent=2)
                self.logger.info(f"Saved configuration to {config_path}")
                
            elif file_ext in [".yaml", ".yml"]:
                try:
                    import yaml
                    with open(config_path, "w") as f:
                        yaml.dump(self.config, f)
                    self.logger.info(f"Saved configuration to {config_path}")
                except ImportError:
                    self.logger.error("PyYAML not installed, cannot save YAML configuration")
                    return False
            else:
                self.logger.warning(f"Unsupported configuration file format: {file_ext}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {config_path}: {str(e)}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Dictionary of all configuration values
        """
        return dict(self.config)