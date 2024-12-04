import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from page2prompt.components.meta_chain import MetaChain

class TestMetaChain(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.meta_chain = MetaChain()

    @patch('page2prompt.components.meta_chain.RunnableSequence')
    async def test_generate_prompt_processing(self, mock_runnable_sequence):
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
            "director_style": "Test Director Style",
            "style_prefix": "Prefix "
        }

        # Mock the LLM response
        mock_llm_response = """
        *** Concise: Close-up of Subject1's expressive face.

        *** Normal: A tight close-up shot focuses on Subject1's face, capturing nuanced expressions.

        *** Detailed: The camera frames a striking close-up of Subject1, filling the frame with their face. Every detail is in sharp focus, from the subtle creases around their eyes to the intensity in their gaze.
        """

        # Set up the mock for RunnableSequence
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = MagicMock(content=mock_llm_response)
        mock_runnable_sequence.return_value = mock_chain

        result = await self.meta_chain.generate_prompt(**test_input)

        # Assert that the result contains the expected keys
        self.assertIn("concise", result)
        self.assertIn("normal", result)
        self.assertIn("detailed", result)
        self.assertIn("structured", result)

        # Assert that the prompts contain expected content
        self.assertIn("Close-up of Subject1's expressive face", result["concise"])
        self.assertIn("A tight close-up shot focuses on Subject1's face", result["normal"])
        self.assertIn("The camera frames a striking close-up of Subject1", result["detailed"])

        # Assert that the style prefix is applied
        self.assertTrue(all(prompt.startswith("Prefix ") for prompt in result.values() if prompt != result["structured"]))

    @patch('page2prompt.components.meta_chain.RunnableSequence')
    async def test_generate_prompt_unexpected_format(self, mock_runnable_sequence):
        test_input = {
            "style": "Test Style",
            "highlighted_text": "Test Highlight",
            "shot_description": "Test Shot",
            "directors_notes": "Test Notes",
            "script": "Test Script",
            "stick_to_script": True,
            "end_parameters": "Test End"
        }

        # Mock an unexpected LLM response format
        mock_unexpected_response = "Unexpected response without proper formatting"

        # Set up the mock for RunnableSequence
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = MagicMock(content=mock_unexpected_response)
        mock_runnable_sequence.return_value = mock_chain

        result = await self.meta_chain.generate_prompt(**test_input)

        # Assert that the method handled the unexpected format gracefully
        self.assertTrue(all("Error processing LLM response" in prompt for prompt in result.values()))

if __name__ == '__main__':
    unittest.main()
