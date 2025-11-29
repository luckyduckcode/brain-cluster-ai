"""
Motor Cortex: Executes actions on the environment.

This module translates high-level decisions into concrete system actions.
It includes safety checks and sandboxing to prevent destructive operations.
"""

import subprocess
import os
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Action:
    """Represents an executable action."""
    type: str
    params: Dict[str, Any]
    source: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + 'Z'


class MotorCortex:
    """
    Executes actions and returns outcomes.
    
    Supported Actions:
    - read_file: Read content of a file
    - write_file: Write content to a file
    - list_dir: List directory contents
    - run_command: Run a shell command (safely)
    - no_op: Do nothing
    """
    
    def __init__(self, sandbox_dir: str = "./sandbox"):
        """
        Initialize Motor Cortex.
        
        Args:
            sandbox_dir: Directory to restrict file operations to (for safety)
        """
        self.sandbox_dir = os.path.abspath(sandbox_dir)
        self.history: List[Dict[str, Any]] = []
        
        # Ensure sandbox exists
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        logger.info(f"Motor Cortex initialized (sandbox: {self.sandbox_dir})")
    
    def execute(self, action: Action) -> Dict[str, Any]:
        """
        Execute an action and return the result.
        
        Args:
            action: Action object to execute
            
        Returns:
            Dictionary containing execution result/outcome
        """
        logger.info(f"Executing action: {action.type} (source: {action.source})")
        
        start_time = datetime.utcnow()
        result = {"status": "failed", "output": "", "error": None}
        
        try:
            if action.type == "read_file":
                result = self._read_file(action.params)
            elif action.type == "write_file":
                result = self._write_file(action.params)
            elif action.type == "list_dir":
                result = self._list_dir(action.params)
            elif action.type == "run_command":
                result = self._run_command(action.params)
            elif action.type == "no_op":
                result = {"status": "success", "output": "No operation performed"}
            else:
                result["error"] = f"Unknown action type: {action.type}"
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            result["error"] = str(e)
        
        # Record outcome
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        outcome = {
            "action": action.type,
            "params": action.params,
            "result": result,
            "timestamp": end_time.isoformat() + 'Z',
            "duration": duration
        }
        
        self.history.append(outcome)
        return outcome
    
    def _validate_path(self, path: str) -> str:
        """Ensure path is within sandbox."""
        # Allow absolute paths if explicitly enabled (disabled for now)
        # For prototype, we map everything relative to sandbox
        
        clean_path = path.lstrip("/")
        full_path = os.path.abspath(os.path.join(self.sandbox_dir, clean_path))
        
        if not full_path.startswith(self.sandbox_dir):
            raise ValueError(f"Access denied: Path {path} is outside sandbox {self.sandbox_dir}")
            
        return full_path
    
    def _read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file."""
        path = params.get("path")
        if not path:
            return {"status": "failed", "error": "Missing path parameter"}
            
        full_path = self._validate_path(path)
        
        if not os.path.exists(full_path):
            return {"status": "failed", "error": "File not found"}
            
        with open(full_path, 'r') as f:
            content = f.read()
            
        return {"status": "success", "output": content}
    
    def _write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file."""
        path = params.get("path")
        content = params.get("content", "")
        
        if not path:
            return {"status": "failed", "error": "Missing path parameter"}
            
        full_path = self._validate_path(path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
            
        return {"status": "success", "output": f"Wrote {len(content)} bytes to {path}"}
    
    def _list_dir(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List directory contents."""
        path = params.get("path", ".")
        full_path = self._validate_path(path)
        
        if not os.path.exists(full_path):
            return {"status": "failed", "error": "Directory not found"}
            
        items = os.listdir(full_path)
        return {"status": "success", "output": items}
    
    def _run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a shell command."""
        command = params.get("command")
        if not command:
            return {"status": "failed", "error": "Missing command parameter"}
            
        # Safety check: simplistic blacklist
        blacklist = ["rm -rf", "mkfs", "dd", ":(){ :|:& };:"]
        for bad in blacklist:
            if bad in command:
                return {"status": "failed", "error": "Command blocked by safety filter"}
        
        # Run command
        try:
            # Run in sandbox directory
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.sandbox_dir,
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            status = "success" if result.returncode == 0 else "failed"
            output = result.stdout if result.returncode == 0 else result.stderr
            
            return {"status": status, "output": output.strip()}
            
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "Command timed out"}
