"""
Tool Integration for Motor Cortex

Extends the motor cortex with intelligent tool selection and execution.
The brain can now choose and use appropriate tools to solve problems.
"""

import logging
from typing import Dict, Any, Optional, List
from digital_cortex.tools import tool_registry, ToolResult
from digital_cortex.motor_cortex.executor import MotorCortex, Action

logger = logging.getLogger(__name__)


class ToolIntegratedMotorCortex(MotorCortex):
    """
    Extended motor cortex with tool integration capabilities.

    Can intelligently select and execute tools based on task requirements.
    """

    def __init__(self, sandbox_dir: str = "./sandbox"):
        super().__init__(sandbox_dir)
        self.available_tools = tool_registry.list_tools()
        logger.info(f"Tool-integrated motor cortex initialized with {len(self.available_tools)} tools")

    def select_tool(self, task_description: str) -> Optional[str]:
        """
        Intelligently select the most appropriate tool for a task.

        Args:
            task_description: Description of the task to perform

        Returns:
            Name of the selected tool, or None if no suitable tool found
        """
        task_lower = task_description.lower()

        # Simple keyword-based tool selection
        # This could be enhanced with ML-based tool selection
        
        # Check for explicit tool names first
        if 'calculator' in task_lower:
            return 'calculator'
        elif 'web_search' in task_lower or 'search' in task_lower:
            return 'web_search'
        elif 'code_execution' in task_lower or ('execute' in task_lower and 'code' in task_lower):
            return 'code_execution'
        elif 'knowledge_base' in task_lower:
            return 'knowledge_base'
        
        # Fallback to general keywords
        if any(word in task_lower for word in ['calculate', 'math', 'compute', 'solve', 'equation']):
            return 'calculator'
        elif any(word in task_lower for word in ['search', 'web', 'internet', 'find', 'lookup']):
            return 'web_search'
        elif any(word in task_lower for word in ['run', 'execute', 'code', 'program', 'script']):
            return 'code_execution'
        elif any(word in task_lower for word in ['fact', 'knowledge', 'convert', 'unit']):
            return 'knowledge_base'

        return None

    def execute_with_tools(self, task: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task using the most appropriate tool.

        Args:
            task: Description of the task
            params: Additional parameters for the task

        Returns:
            Execution result
        """
        if params is None:
            params = {}

        # Try to select an appropriate tool
        tool_name = self.select_tool(task)

        if tool_name:
            logger.info(f"Selected tool '{tool_name}' for task: {task}")

            # Execute with the selected tool
            tool_result = tool_registry.execute_tool(tool_name, params)

            # Convert ToolResult to the expected format
            result = {
                "action": f"tool_{tool_name}",
                "tool_used": tool_name,
                "task": task,
                "result": {
                    "status": "success" if tool_result.success else "failed",
                    "output": tool_result.output,
                    "error": tool_result.error
                },
                "timestamp": "now",  # Would be set properly in production
                "duration": 0.0
            }

            self.history.append(result)
            return result

        # Fall back to regular motor cortex actions
        logger.info(f"No suitable tool found for task: {task}, using standard actions")
        return self._handle_standard_action(task, params)

    def _handle_standard_action(self, task: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tasks that don't require specialized tools."""
        # Map task descriptions to standard actions
        task_lower = task.lower()

        if 'read file' in task_lower or 'open file' in task_lower:
            action = Action("read_file", params, "tool_integration")
        elif 'write file' in task_lower or 'save file' in task_lower:
            action = Action("write_file", params, "tool_integration")
        elif 'list directory' in task_lower or 'show files' in task_lower:
            action = Action("list_dir", params, "tool_integration")
        elif 'run command' in task_lower or 'execute command' in task_lower:
            action = Action("run_command", params, "tool_integration")
        else:
            # Default to no-op
            action = Action("no_op", {}, "tool_integration")

        return self.execute(action)

    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools."""
        return self.available_tools.copy()

    def demonstrate_tools(self) -> Dict[str, Any]:
        """Demonstrate all available tools with example usage."""
        demonstrations = {}

        # Calculator demo
        calc_result = tool_registry.execute_tool("calculator", {"expression": "2**10 + sqrt(144)"})
        demonstrations["calculator"] = {
            "description": "Mathematical calculations",
            "example": "2**10 + sqrt(144)",
            "result": calc_result.output if calc_result.success else calc_result.error
        }

        # Web search demo (would need internet)
        demonstrations["web_search"] = {
            "description": "Web search capabilities",
            "example": "current weather in Tokyo",
            "note": "Requires internet connection"
        }

        # Code execution demo
        code_result = tool_registry.execute_tool("code_execution", {
            "language": "python",
            "code": "print('Hello from tool execution!')\nx = 42\nx * 2"
        })
        demonstrations["code_execution"] = {
            "description": "Safe code execution",
            "example": "print('Hello!'); x = 42; x * 2",
            "result": code_result.output if code_result.success else code_result.error
        }

        # Knowledge base demo
        kb_result = tool_registry.execute_tool("knowledge_base", {
            "type": "math_facts",
            "query": "pi"
        })
        demonstrations["knowledge_base"] = {
            "description": "Knowledge queries",
            "example": "math_facts: pi",
            "result": kb_result.output if kb_result.success else kb_result.error
        }

        return demonstrations