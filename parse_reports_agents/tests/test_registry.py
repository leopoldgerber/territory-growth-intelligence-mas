import unittest

from agent_app.agent.action_result import success_result
from agent_app.agent_tools.tool_registry import ToolRegistry, call_tool, register_tool, tool_names


class RegistryTest(unittest.TestCase):
    def test_call_tool(self) -> None:
        """Test tool call.
        Args:
            self (RegistryTest): Test case instance."""
        registry = ToolRegistry()
        register_tool(registry, 'sample_tool', lambda value: success_result('ok', {'value': value}))
        result = call_tool(registry, 'sample_tool', {'value': 'x'})
        self.assertTrue(result.success)
        self.assertEqual(result.evidence['value'], 'x')
        self.assertEqual(tool_names(registry), ['sample_tool'])

    def test_missing_tool(self) -> None:
        """Test missing tool.
        Args:
            self (RegistryTest): Test case instance."""
        registry = ToolRegistry()
        result = call_tool(registry, 'missing_tool', {})
        self.assertFalse(result.success)
