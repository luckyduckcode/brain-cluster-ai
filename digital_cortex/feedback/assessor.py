"""
Outcome Assessor: Evaluates the results of actions.

This module compares the predicted outcome with the actual result
to generate a success/failure signal.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Assessment:
    """Result of an outcome assessment."""
    success: bool
    score: float  # -1.0 to 1.0
    feedback: str
    metrics: Dict[str, Any]


class OutcomeAssessor:
    """
    Evaluates action outcomes against expectations.
    """
    
    def assess(self, 
               action_type: str, 
               params: Dict[str, Any], 
               result: Dict[str, Any], 
               expectation: Optional[str] = None) -> Assessment:
        """
        Assess the outcome of an action.
        
        Args:
            action_type: Type of action performed
            params: Parameters used
            result: Result dictionary from MotorCortex
            expectation: Optional description of expected outcome
            
        Returns:
            Assessment object
        """
        logger.info(f"Assessing outcome for {action_type}")
        
        # Basic assessment: Did the action succeed technically?
        technical_success = result.get("status") == "success"
        
        if not technical_success:
            return Assessment(
                success=False,
                score=-0.5,
                feedback=f"Action failed: {result.get('error')}",
                metrics={"technical_success": False}
            )
        
        # Advanced assessment based on action type
        if action_type == "read_file":
            return self._assess_read(result, expectation)
        elif action_type == "write_file":
            return self._assess_write(result, expectation)
        elif action_type == "run_command":
            return self._assess_command(result, expectation)
        
        # Default success
        return Assessment(
            success=True,
            score=0.5,
            feedback="Action completed successfully",
            metrics={"technical_success": True}
        )
    
    def _assess_read(self, result: Dict[str, Any], expectation: Optional[str]) -> Assessment:
        """Assess file read outcome."""
        content = result.get("output", "")
        size = len(content)
        
        if size == 0:
            return Assessment(
                success=True, # Technically successful even if empty
                score=0.1,
                feedback="File read successfully but was empty",
                metrics={"size": 0}
            )
            
        return Assessment(
            success=True,
            score=0.8,
            feedback=f"Read {size} bytes successfully",
            metrics={"size": size}
        )
    
    def _assess_write(self, result: Dict[str, Any], expectation: Optional[str]) -> Assessment:
        """Assess file write outcome."""
        return Assessment(
            success=True,
            score=1.0,
            feedback=result.get("output", "Write successful"),
            metrics={}
        )
    
    def _assess_command(self, result: Dict[str, Any], expectation: Optional[str]) -> Assessment:
        """Assess command execution."""
        output = result.get("output", "")
        
        # If we had an expectation, check if it appears in output
        if expectation and expectation.lower() in output.lower():
            return Assessment(
                success=True,
                score=1.0,
                feedback="Command succeeded and matched expectation",
                metrics={"match": True}
            )
            
        return Assessment(
            success=True,
            score=0.7,
            feedback="Command executed successfully",
            metrics={"output_len": len(output)}
        )
