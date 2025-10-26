"""
Configuration Manager
Handles loading and managing application configuration from settings.json
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration with defaults and validation."""
    
    # Default configuration in case file is missing or invalid
    DEFAULT_CONFIG = {
        "scan_path": ".",
        "exclude_dirs": [".git", "node_modules", "__pycache__", "venv"],
        "project_indicators": ["REQUIREMENTS.md", "TODO.md", "README.md"],
        "auto_scan_interval_seconds": 300,
        "logging": {
            "level": "INFO",
            "file": "logs/parallel-dev.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "ui": {
            "window_width": 1400,
            "window_height": 900,
            "theme": "light"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, looks for config/settings.json
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> str:
        """Find the configuration file in standard locations."""
        # Try relative to current directory
        possible_paths = [
            "config/settings.json",
            "../config/settings.json",
            os.path.join(os.path.dirname(__file__), "../../config/settings.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path even if it doesn't exist
        return "config/settings.json"    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file with error handling.
        
        Returns:
            Dictionary containing configuration settings
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                
                # Merge with defaults to ensure all keys exist
                return self._merge_with_defaults(config)
            else:
                self.logger.warning(
                    f"Configuration file not found at {self.config_path}. "
                    f"Using default configuration."
                )
                return self.DEFAULT_CONFIG.copy()
                
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Invalid JSON in configuration file {self.config_path}: {e}. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            self.logger.error(
                f"Error loading configuration from {self.config_path}: {e}. "
                f"Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded configuration with defaults to ensure all keys exist.
        
        Args:
            config: Loaded configuration dictionary
            
        Returns:
            Merged configuration with all required keys
        """
        merged = self.DEFAULT_CONFIG.copy()
        
        # Deep merge for nested dictionaries
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (supports nested keys with dots, e.g., 'ui.window_width')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            # Support nested keys with dot notation
            keys = key.split('.')
            value = self.config            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                    if value is None:
                        return default
                else:
                    return default
            
            return value if value is not None else default
            
        except Exception as e:
            self.logger.error(f"Error getting configuration key '{key}': {e}")
            return default
    
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to {self.config_path}: {e}")
            return False
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports nested keys with dots)
            value: Value to set
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the nested dictionary
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the final value
            config[keys[-1]] = value
            self.logger.debug(f"Configuration key '{key}' set to {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting configuration key '{key}': {e}")
    
    def validate_paths(self) -> bool:
        """
        Validate that configured paths exist or can be created.
        
        Returns:
            True if all paths are valid, False otherwise
        """
        try:
            scan_path = self.get('scan_path')
            if not os.path.exists(scan_path):
                self.logger.warning(f"Scan path does not exist: {scan_path}")
                return False
            
            # Ensure log directory exists
            log_file = self.get('logging.file')
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                self.logger.info(f"Created log directory: {log_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating paths: {e}")
            return False
