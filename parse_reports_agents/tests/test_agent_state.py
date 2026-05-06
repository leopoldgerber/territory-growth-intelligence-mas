import tempfile
import unittest
from pathlib import Path

from agent_app.agent.agent_state import create_state, load_state, save_state


class AgentStateTest(unittest.TestCase):
    def test_save_state(self) -> None:
        """Test state serialization.
        Args:
            self (AgentStateTest): Test case instance."""
        state = create_state('download', ['example.com'], ['Apr'], ['visits'])
        state.current_domain = 'example.com'
        with tempfile.TemporaryDirectory() as temp_name:
            state_path = Path(temp_name) / 'agent_state.json'
            saved_path = save_state(state, state_path)
            loaded_data = load_state(saved_path)
        self.assertEqual(loaded_data['current_domain'], 'example.com')
        self.assertEqual(loaded_data['domain_list'], ['example.com'])
