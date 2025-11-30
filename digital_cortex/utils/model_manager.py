"""
Model Manager: Dynamic model selection and fallback handling.
"""

import logging
from typing import Optional, List, Dict, Any
from .config import get_config

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages model selection based on task complexity and availability.
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize model manager.
        
        Args:
            config_manager: Optional ConfigManager instance
        """
        self.config = config_manager or get_config()
        self.model_history: List[Dict[str, Any]] = []
        
        logger.info("ModelManager initialized")
    
    def select_model(self, 
                    complexity: str = "default",
                    task_type: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Select the best model for a given task.
        
        Args:
            complexity: Complexity level ("default", "high_complexity", "fast")
            task_type: Optional task type hint
            context: Optional context information
            
        Returns:
            Model name
        """
        # Get model from config
        model = self.config.get_model(complexity)
        
        # Apply task-specific overrides
        if task_type == "meta_cognition" and complexity == "default":
            # Meta-cognition benefits from higher complexity
            model = self.config.get_model("high_complexity")
        elif task_type == "quick_response":
            # Quick responses use fast model
            model = self.config.get_model("fast")
        
        # Check context for urgency
        if context and context.get("urgency", 0) > 0.8:
            # High urgency: use fast model
            model = self.config.get_model("fast")
        
        logger.debug(f"Selected model: {model} (complexity={complexity}, task={task_type})")
        
        # Record selection
        self.model_history.append({
            "model": model,
            "complexity": complexity,
            "task_type": task_type,
            "context": context
        })
        
        return model
    
    def get_fallback_models(self, primary_model: str) -> List[str]:
        """
        Get fallback models if primary fails.
        
        Args:
            primary_model: The primary model that failed
            
        Returns:
            List of fallback model names
        """
        # Define fallback chain
        fallback_chain = {
            self.config.get_model("high_complexity"): [
                self.config.get_model("default"),
                self.config.get_model("fast")
            ],
            self.config.get_model("default"): [
                self.config.get_model("fast")
            ],
            self.config.get_model("fast"): []
        }
        
        return fallback_chain.get(primary_model, [self.config.get_model("default")])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model usage statistics."""
        if not self.model_history:
            return {"total_selections": 0}
        
        from collections import Counter
        model_counts = Counter(h["model"] for h in self.model_history)
        
        return {
            "total_selections": len(self.model_history),
            "model_distribution": dict(model_counts),
            "most_used": model_counts.most_common(1)[0] if model_counts else None
        }
