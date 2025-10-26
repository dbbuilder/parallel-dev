"""
Configuration Management Module
Handles loading and managing application configuration from config.json and environment variables.
Author: DBBuilder
Date: 2025-10-25
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    Configuration manager for the ParallelDev application.
    Loads configuration from config.json and allows environment variable overrides.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load configuration from JSON file.
        Raises exception if file cannot be loaded.
        """
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            self.logger.info(f"Configuration loaded successfully from {self.config_path}")
        
        except FileNotFoundError as e:
            self.logger.error(f"Configuration file not found: {e}")
            raise
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {e}")
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error loading configuration: {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation for nested keys.
        
        Args:
            key_path: Dot-separated path to the configuration value (e.g., 'database.path')
            default: Default value to return if key not found
        
        Returns:
            The configuration value or default if not found
        """
        keys = key_path.split('.')
        value = self.config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        
        except (KeyError, TypeError):
            self.logger.debug(f"Configuration key not found: {key_path}, using default: {default}")
            return default
    
    def get_env_or_config(self, env_var: str, config_key: str, default: Any = None) -> Any:
        """
        Get value from environment variable first, fall back to config, then default.
        
        Args:
            env_var: Environment variable name
            config_key: Dot-separated configuration key path
            default: Default value if neither env nor config found
        
        Returns:
            Value from environment, config, or default
        """
        # Check environment variable first
        env_value = os.getenv(env_var)
        if env_value is not None:
            self.logger.debug(f"Using environment variable {env_var}")
            return env_value
        
        # Fall back to configuration
        config_value = self.get(config_key, None)
        if config_value is not None:
            return config_value
        
        # Use default
        self.logger.debug(f"Using default value for {env_var}/{config_key}: {default}")
        return default
    
    def reload(self) -> None:
        """
        Reload configuration from file.
        Useful for hot-reloading configuration changes.
        """
        self.logger.info("Reloading configuration...")
        self._load_config()
    
    def validate(self) -> bool:
        """
        Validate that required configuration keys are present and valid.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = [
            'scanning.scan_directory',
            'database.path',
            'server.host',
            'server.port'
        ]
        
        is_valid = True
        
        for key in required_keys:
            value = self.get(key)
            if value is None:
                self.logger.error(f"Required configuration key missing: {key}")
                is_valid = False
        
        # Validate scan directory exists or can be created
        scan_dir = self.get('scanning.scan_directory')
        if scan_dir:
            scan_path = Path(scan_dir)
            if not scan_path.exists():
                self.logger.warning(f"Scan directory does not exist: {scan_dir}")
        
        # Validate database directory exists or can be created
        db_path = self.get('database.path')
        if db_path:
            db_dir = Path(db_path).parent
            if not db_dir.exists():
                try:
                    db_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created database directory: {db_dir}")
                except Exception as e:
                    self.logger.error(f"Failed to create database directory: {e}")
                    is_valid = False
        
        return is_valid
    
    def __repr__(self) -> str:
        """String representation of the configuration."""
        return f"Config(path='{self.config_path}', keys={list(self.config_data.keys())})"


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_path: str = "config.json") -> Config:
    """
    Get the global configuration instance (singleton pattern).
    
    Args:
        config_path: Path to configuration file (only used on first call)
    
    Returns:
        Global Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_path)
    
    return _config_instance


def reload_config() -> None:
    """
    Reload the global configuration instance.
    """
    global _config_instance
    
    if _config_instance is not None:
        _config_instance.reload()
