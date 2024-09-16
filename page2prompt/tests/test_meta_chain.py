import unittest
from unittest.mock import patch, MagicMock
from page2prompt.components.meta_chain import MetaChain

class TestMetaChain(unittest.TestCase):
    def setUp(self):
        self.meta_chain = MetaChain()

    @patch('page2prompt.components.meta_chain.ChatOpenAI')
    async def test_generate_prompt(self, mock_chat_openai):
        # Mock the LLM response
        mock_generation = MagicMock()
        mock_generation.generations = [[MagicMock(text="Concise prompt\n\nNormal prompt\n\nDetailed prompt")]]
        mock_chat_openai.return_value.agenerate.return_value = mock_generation

        # Test input
        test_input = {
            "style": "Test Style",
            "highlighted_text": "Test Highlight",
            "shot_description": "Test Shot",
            "directors_notes": "Test Notes",
            "script": "Test Script",
            "stick_to_script": True,
            "end_parameters": "Test End",
            "active_subjects": [{"Name": "Subject1"}, {"Name": "Subject2"}],
            "full_script": "Full Test Script",
            "shot_configuration": {
                "shot": "Close-up",
                "move": "Static",
                "size": "Medium",
                "framing": "Center",
                "depth_of_field": "Shallow"
            },
            "length": "normal",
            "director_style": "Test Director Style"
        }

        result = await self.meta_chain.generate_prompt(**test_input)

        # Assert that the result contains the expected keys
        self.assertIn("concise", result)
        self.assertIn("normal", result)
        self.assertIn("detailed", result)
        self.assertIn("structured", result)

        # Assert that the prompts are as expected
        self.assertEqual(result["concise"], "Concise prompt")
        self.assertEqual(result["normal"], "Normal prompt")
        self.assertEqual(result["detailed"], "Detailed prompt")

    @patch('page2prompt.components.meta_chain.ChatOpenAI')
    async def test_generate_prompt_error(self, mock_chat_openai):
        # Mock an error in LLM generation
        mock_chat_openai.return_value.agenerate.side_effect = Exception("Test error")

        # Test input (can be minimal for this test)
        test_input = {"style": "Test Style"}

        result = await self.meta_chain.generate_prompt(**test_input)

        # Assert that the result contains error messages
        self.assertIn("Error generating concise prompt", result["concise"])
        self.assertIn("Error generating normal prompt", result["normal"])
        self.assertIn("Error generating detailed prompt", result["detailed"])
        self.assertIn("Error: Test error", result["structured"])

if __name__ == '__main__':
    unittest.main()
