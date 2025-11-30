"""
Configuration Manager: Load and manage system configuration.
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages system configuration from YAML files.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config file (defaults to ./config.yaml)
        """
        if config_path is None:
            # Look for config.yaml in project root
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        
        self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self.config = self._get_defaults()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            self.config = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "models": {
                "default": "llama3.2:1b",
                "high_complexity": "llama3.2:3b",
                "fast": "llama3.2:1b"
            },
            "ollama": {
                "url": "http://localhost:11434",
                "timeout": 60
            },
            "neurons": {
                "default_temperature": 0.7,
                "confidence_extraction": True
            },
            "cache": {
                "enabled": True,
                "max_size": 100,
                "similarity_threshold": 0.95
            },
            "consensus": {
                "dbscan_eps": 0.3,
                "dbscan_min_samples": 2,
                "max_capacity": 100
            },
            "memory": {
                "room_capacity": 512
            },
            "meta_cognition": {
                "confusion_threshold": 0.7,
                "uncertainty_threshold": 0.6
            },
            "motor_cortex": {
                "sandbox_dir": "./sandbox",
                "command_timeout": 5
            },
            "learning": {
                "learning_rate": 0.1,
                "weight_min": 0.1,
                "weight_max": 2.0,
                "storage_path": "neuron_weights.json"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., "models.default")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_model(self, complexity: str = "default") -> str:
        """
        Get model name for given complexity level.
        
        Args:
            complexity: One of "default", "high_complexity", "fast"
            
        Returns:
            Model name
        """
        return self.get(f"models.{complexity}", self.get("models.default"))
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")


# Global config instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
