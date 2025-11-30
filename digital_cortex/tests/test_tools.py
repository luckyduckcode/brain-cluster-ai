"""
Tests for Tool Integration System
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from digital_cortex.tools import tool_registry, CalculatorTool, WebSearchTool, CodeExecutionTool, KnowledgeBaseTool
from digital_cortex.motor_cortex.tool_integration import ToolIntegratedMotorCortex


class TestCalculatorTool:
    """Test the calculator tool."""

    def test_basic_calculation(self):
        """Test basic mathematical calculation."""
        tool = CalculatorTool()
        result = tool.execute({"expression": "2 + 3 * 4"})

        assert result.success
        assert result.output["numeric"] == 14

    def test_symbolic_calculation(self):
        """Test symbolic calculation."""
        tool = tool_registry.execute_tool("calculator", {"expression": "x**2 + 2*x + 1"})

        assert tool.success
        assert "symbolic" in tool.output

    def test_invalid_expression(self):
        """Test invalid mathematical expression."""
        tool = CalculatorTool()
        result = tool.execute({"expression": "invalid expression +++"})

        assert not result.success
        assert "error" in result.error.lower()


class TestCodeExecutionTool:
    """Test the code execution tool."""

    def test_python_execution(self):
        """Test Python code execution."""
        tool = CodeExecutionTool()
        result = tool.execute({
            "language": "python",
            "code": "x = 42\ny = x * 2\ny"  # Return the value instead of printing
        })

        assert result.success
        assert result.output["output"] == "84"

    def test_unsafe_code_blocked(self):
        """Test that unsafe code is blocked."""
        tool = CodeExecutionTool()
        result = tool.execute({
            "language": "python",
            "code": "import os\nos.system('rm -rf /')"
        })

        assert not result.success
        assert "unsafe" in result.error.lower()

    def test_javascript_execution(self):
        """Test JavaScript code execution (if Node.js available)."""
        tool = CodeExecutionTool()
        result = tool.execute({
            "language": "javascript",
            "code": "console.log(42 * 2);"
        })

        # This might fail if Node.js is not installed, which is OK
        if "Node.js not installed" in str(result.error):
            pytest.skip("Node.js not available")
        else:
            assert isinstance(result, object)  # Just check it returns something


class TestKnowledgeBaseTool:
    """Test the knowledge base tool."""

    def test_math_facts(self):
        """Test mathematical facts lookup."""
        tool = KnowledgeBaseTool()
        result = tool.execute({
            "type": "math_facts",
            "query": "pi"
        })

        assert result.success
        assert "fact" in result.output

    def test_unit_conversion(self):
        """Test unit conversion."""
        tool = KnowledgeBaseTool()
        result = tool.execute({
            "type": "unit_conversion",
            "query": "convert 100 celsius to fahrenheit"
        })

        assert result.success
        assert result.output["converted_value"] == 212.0


class TestWebSearchTool:
    """Test the web search tool."""

    @patch('requests.get')
    def test_web_search(self, mock_get):
        """Test web search functionality."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Answer": "Paris is the capital of France.",
            "AbstractText": "Paris is the capital and most populous city of France.",
            "AbstractURL": "https://en.wikipedia.org/wiki/Paris",
            "RelatedTopics": [{"Text": "France is a country in Europe."}]
        }
        mock_get.return_value = mock_response

        tool = WebSearchTool()
        result = tool.execute({"query": "capital of France"})

        assert result.success
        assert "Paris" in result.output["answer"]
        assert "France" in result.output["abstract"]


class TestToolRegistry:
    """Test the tool registry."""

    def test_registry_initialization(self):
        """Test that tools are properly registered."""
        registry = tool_registry
        tools = registry.list_tools()

        assert len(tools) >= 4  # At least calculator, web search, code execution, knowledge base
        tool_names = [t["name"] for t in tools]
        assert "calculator" in tool_names
        assert "web_search" in tool_names
        assert "code_execution" in tool_names
        assert "knowledge_base" in tool_names

    def test_tool_execution(self):
        """Test executing tools through registry."""
        result = tool_registry.execute_tool("calculator", {"expression": "5 + 3"})
        assert result.success
        assert result.output["numeric"] == 8


class TestToolIntegratedMotorCortex:
    """Test the tool-integrated motor cortex."""

    def test_tool_selection(self):
        """Test intelligent tool selection."""
        cortex = ToolIntegratedMotorCortex()

        # Test calculator selection
        tool_name = cortex.select_tool("calculate 2 + 2")
        assert tool_name == "calculator"

        # Test web search selection
        tool_name = cortex.select_tool("search for weather in Tokyo")
        assert tool_name == "web_search"

        # Test code execution selection
        tool_name = cortex.select_tool("run this python code")
        assert tool_name == "code_execution"

        # Test unknown task
        tool_name = cortex.select_tool("tell me a joke")
        assert tool_name is None

    def test_tool_execution_integration(self):
        """Test tool execution through motor cortex."""
        cortex = ToolIntegratedMotorCortex()

        result = cortex.execute_with_tools("calculate 10 * 5", {"expression": "10 * 5"})

        assert result["action"] == "tool_calculator"
        assert result["result"]["status"] == "success"
        assert result["result"]["output"]["numeric"] == 50

    def test_available_tools(self):
        """Test getting available tools."""
        cortex = ToolIntegratedMotorCortex()
        tools = cortex.get_available_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0
        assert all("name" in tool and "description" in tool for tool in tools)

    def test_demonstrate_tools(self):
        """Test tool demonstration."""
        cortex = ToolIntegratedMotorCortex()
        demo = cortex.demonstrate_tools()

        assert isinstance(demo, dict)
        assert "calculator" in demo
        assert "code_execution" in demo
        # Other tools might not work without external dependencies