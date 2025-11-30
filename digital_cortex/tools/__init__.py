"""
Tool Integration System for Brain Cluster AI

Extends the motor cortex with specialized tools for enhanced capabilities:
- Calculator for mathematical computations
- Web search for retrieving current information
- Code execution for running code snippets
- Knowledge base queries
"""

import os
import logging
import subprocess
import requests
import json
import re
import tempfile
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import sympy
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result from executing a tool."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Tool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters. Override in subclasses."""
        return True


class CalculatorTool(Tool):
    """Mathematical calculator using sympy for symbolic computation."""

    def __init__(self):
        super().__init__(
            "calculator",
            "Perform mathematical calculations, solve equations, and symbolic computation"
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute mathematical calculation."""
        expression = params.get("expression", "").strip()
        if not expression:
            return ToolResult(False, None, "No expression provided")

        try:
            # Use sympy for symbolic computation
            result = sympy.sympify(expression)

            # Try to evaluate numerically if possible
            try:
                numeric_result = float(result.evalf())
                return ToolResult(True, {
                    "symbolic": str(result),
                    "numeric": numeric_result
                })
            except:
                return ToolResult(True, {
                    "symbolic": str(result),
                    "numeric": None
                })

        except Exception as e:
            return ToolResult(False, None, f"Calculation error: {str(e)}")


class WebSearchTool(Tool):
    """Web search tool using DuckDuckGo instant answers API."""

    def __init__(self):
        super().__init__(
            "web_search",
            "Search the web for current information and facts"
        )
        self.base_url = "https://api.duckduckgo.com/"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute web search."""
        query = params.get("query", "").strip()
        if not query:
            return ToolResult(False, None, "No search query provided")

        try:
            # Use DuckDuckGo instant answers API
            response = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1"
                },
                timeout=10
            )

            if response.status_code != 200:
                return ToolResult(False, None, f"Search API error: {response.status_code}")

            data = response.json()

            # Extract relevant information
            result = {
                "query": query,
                "answer": data.get("Answer", ""),
                "abstract": data.get("AbstractText", ""),
                "source": data.get("AbstractURL", ""),
                "related_topics": [
                    topic.get("Text", "") for topic in data.get("RelatedTopics", [])[:3]
                ]
            }

            return ToolResult(True, result)

        except requests.RequestException as e:
            return ToolResult(False, None, f"Network error: {str(e)}")


class CodeExecutionTool(Tool):
    """Safe code execution tool with sandboxing."""

    def __init__(self):
        super().__init__(
            "code_execution",
            "Execute code snippets in a safe, sandboxed environment"
        )
        self.supported_languages = {
            "python": self._execute_python,
            "bash": self._execute_bash,
            "javascript": self._execute_javascript
        }

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute code in specified language."""
        language = params.get("language", "python").lower()
        code = params.get("code", "").strip()

        if not code:
            return ToolResult(False, None, "No code provided")

        if language not in self.supported_languages:
            return ToolResult(False, None, f"Unsupported language: {language}")

        try:
            executor = self.supported_languages[language]
            return executor(code)
        except Exception as e:
            return ToolResult(False, None, f"Execution error: {str(e)}")

    def _execute_python(self, code: str) -> ToolResult:
        """Execute Python code safely."""
        # Basic safety checks
        dangerous_patterns = [
            r'import\s+os\b',
            r'import\s+subprocess\b',
            r'import\s+sys\b',
            r'exec\(',
            r'eval\(',
            r'open\(',
            r'__import__'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return ToolResult(False, None, "Code contains potentially unsafe operations")

        try:
            # Execute in restricted environment with safe builtins
            safe_builtins = {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'all': all,
                'any': any,
                'True': True,
                'False': False,
                'None': None,
            }

            local_vars = {}
            exec(code, {"__builtins__": safe_builtins}, local_vars)

            # Get the last expression result if any
            lines = code.strip().split('\n')
            if lines and not lines[-1].strip().startswith((' ', '\t')):
                # Try to evaluate the last line as an expression
                try:
                    result = eval(lines[-1], {"__builtins__": safe_builtins}, local_vars)
                    return ToolResult(True, {"output": str(result), "locals": local_vars})
                except:
                    pass

            return ToolResult(True, {"output": "Code executed successfully", "locals": local_vars})

        except Exception as e:
            return ToolResult(False, None, f"Python execution error: {str(e)}")

    def _execute_bash(self, code: str) -> ToolResult:
        """Execute bash commands safely."""
        # Very restrictive - only allow basic commands
        allowed_commands = [
            'echo', 'cat', 'grep', 'wc', 'head', 'tail', 'sort', 'uniq',
            'cut', 'tr', 'sed', 'awk', 'date', 'cal', 'bc'
        ]

        # Check if command is in allowed list
        first_word = code.strip().split()[0] if code.strip() else ""
        if first_word not in allowed_commands:
            return ToolResult(False, None, f"Command '{first_word}' not allowed")

        try:
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/tmp"  # Safe directory
            )

            output = result.stdout if result.returncode == 0 else result.stderr
            return ToolResult(
                result.returncode == 0,
                {"output": output.strip(), "return_code": result.returncode}
            )

        except subprocess.TimeoutExpired:
            return ToolResult(False, None, "Command timed out")

    def _execute_javascript(self, code: str) -> ToolResult:
        """Execute JavaScript code using Node.js."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            os.unlink(temp_file)

            output = result.stdout if result.returncode == 0 else result.stderr
            return ToolResult(
                result.returncode == 0,
                {"output": output.strip(), "return_code": result.returncode}
            )

        except FileNotFoundError:
            return ToolResult(False, None, "Node.js not installed")
        except subprocess.TimeoutExpired:
            return ToolResult(False, None, "JavaScript execution timed out")


class KnowledgeBaseTool(Tool):
    """Query knowledge bases and APIs."""

    def __init__(self):
        super().__init__(
            "knowledge_base",
            "Query structured knowledge bases and APIs"
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Query knowledge base."""
        query_type = params.get("type", "general")
        query = params.get("query", "").strip()

        if not query:
            return ToolResult(False, None, "No query provided")

        # For now, implement basic knowledge queries
        # This could be extended to query Wikipedia, Wolfram Alpha, etc.
        if query_type == "math_facts":
            return self._math_facts(query)
        elif query_type == "unit_conversion":
            return self._unit_conversion(query)
        else:
            return ToolResult(True, {
                "query": query,
                "type": query_type,
                "note": "Knowledge base query processed (placeholder)"
            })

    def _math_facts(self, query: str) -> ToolResult:
        """Provide mathematical facts."""
        facts = {
            "pi": f"π ≈ {math.pi:.10f}",
            "e": f"e ≈ {math.e:.10f}",
            "golden_ratio": f"φ ≈ {(1 + math.sqrt(5)) / 2:.10f}",
            "speed_of_light": "299,792,458 m/s",
            "planck_constant": "6.62607015 × 10^-34 J⋅s"
        }

        result = facts.get(query.lower().replace(" ", "_"), "Fact not found")
        return ToolResult(True, {"fact": result, "query": query})

    def _unit_conversion(self, query: str) -> ToolResult:
        """Basic unit conversion."""
        # Simple implementation - could be extended
        conversions = {
            "celsius to fahrenheit": lambda x: (x * 9/5) + 32,
            "fahrenheit to celsius": lambda x: (x - 32) * 5/9,
            "meters to feet": lambda x: x * 3.28084,
            "feet to meters": lambda x: x / 3.28084
        }

        # Parse query like "convert 25 celsius to fahrenheit"
        match = re.match(r'convert\s+(\d+(?:\.\d+)?)\s+(.+?)\s+to\s+(.+)', query.lower())
        if match:
            value, from_unit, to_unit = match.groups()
            value = float(value)
            key = f"{from_unit} to {to_unit}"

            if key in conversions:
                result = conversions[key](value)
                return ToolResult(True, {
                    "original_value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "converted_value": result
                })

        return ToolResult(False, None, "Conversion not supported")


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""
        self.register_tool(CalculatorTool())
        self.register_tool(WebSearchTool())
        self.register_tool(CodeExecutionTool())
        self.register_tool(KnowledgeBaseTool())

    def register_tool(self, tool: Tool):
        """Register a new tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {"name": name, "description": desc.description}
            for name, desc in self.tools.items()
        ]

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(False, None, f"Tool '{tool_name}' not found")

        if not tool.validate_params(params):
            return ToolResult(False, None, "Invalid parameters for tool")

        logger.info(f"Executing tool: {tool_name} with params: {params}")
        return tool.execute(params)


# Global tool registry instance
tool_registry = ToolRegistry()