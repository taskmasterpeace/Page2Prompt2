import unittest
from unittest.mock import patch, mock_open
from page2prompt.api.style_management import StyleManager
from page2prompt.models.style import Style

class TestStyleManager(unittest.TestCase):
    def setUp(self):
        self.style_manager = StyleManager("test_styles.csv")

    def test_load_styles(self):
        with patch('page2prompt.api.style_management.read_csv_file') as mock_read_csv:
            mock_read_csv.return_value = [
                {"name": "Test Style", "prefix": "Test Prefix", "suffix": "Test Suffix"}
            ]
            self.style_manager._load_styles()
            self.assertEqual(len(self.style_manager.styles), 1)
            self.assertEqual(self.style_manager.styles[0].name, "Test Style")
            self.assertEqual(self.style_manager.styles[0].prefix, "Test Prefix")
            self.assertEqual(self.style_manager.styles[0].suffix, "Test Suffix")

if __name__ == '__main__':
    unittest.main()

class TestStyleManager(unittest.TestCase):
    def setUp(self):
        self.style_manager = StyleManager("test_styles.csv")

    @patch('page2prompt.api.style_management.read_csv_file')
    def test_load_styles(self, mock_read_csv):
        mock_data = [
            {"name": "Test Style", "prefix": "Test Prefix", "suffix": "Test Suffix", "genre": "Test Genre", "descriptors": "Test Descriptors"}
        ]
        mock_read_csv.return_value = mock_data
        
        # Force reload of styles
        self.style_manager.styles = self.style_manager._load_styles()
        
        self.assertEqual(len(self.style_manager.styles), 1)
        self.assertEqual(self.style_manager.styles[0].name, "Test Style")
        self.assertEqual(self.style_manager.styles[0].prefix, "Test Prefix")
        self.assertEqual(self.style_manager.styles[0].suffix, "Test Suffix")
        self.assertEqual(self.style_manager.styles[0].genre, "Test Genre")
        self.assertEqual(self.style_manager.styles[0].descriptors, "Test Descriptors")

    def test_get_styles(self):
        self.style_manager.styles = [
            Style("Style1", "Prefix1", "Suffix1"),
            Style("Style2", "Prefix2", "Suffix2")
        ]
        styles = self.style_manager.get_styles()
        self.assertEqual(styles, ["Style1", "Style2"])

    def test_get_style(self):
        self.style_manager.styles = [
            Style("Style1", "Prefix1", "Suffix1"),
            Style("Style2", "Prefix2", "Suffix2")
        ]
        style = self.style_manager.get_style("Style1")
        self.assertIsNotNone(style)
        self.assertEqual(style.name, "Style1")

    @patch('page2prompt.api.style_management.write_csv_file')
    def test_add_style(self, mock_write_csv):
        new_style = Style("New Style", "New Prefix", "New Suffix")
        self.style_manager.add_style(new_style)
        self.assertIn(new_style, self.style_manager.styles)
        mock_write_csv.assert_called_once()

    @patch('page2prompt.api.style_management.write_csv_file')
    def test_update_style(self, mock_write_csv):
        self.style_manager.styles = [Style("Style1", "Prefix1", "Suffix1")]
        updated_style = Style("Style1", "Updated Prefix", "Updated Suffix")
        self.style_manager.update_style(updated_style)
        self.assertEqual(self.style_manager.styles[0].prefix, "Updated Prefix")
        mock_write_csv.assert_called_once()

    @patch('page2prompt.api.style_management.write_csv_file')
    def test_delete_style(self, mock_write_csv):
        self.style_manager.styles = [
            Style("Style1", "Prefix1", "Suffix1"),
            Style("Style2", "Prefix2", "Suffix2")
        ]
        self.style_manager.delete_style("Style1")
        self.assertEqual(len(self.style_manager.styles), 1)
        self.assertEqual(self.style_manager.styles[0].name, "Style2")
        mock_write_csv.assert_called_once()

    def test_create_random_style(self):
        random_style = StyleManager.create_random_style()
        self.assertIsInstance(random_style, Style)
        self.assertIsNotNone(random_style.name)
        self.assertIsNotNone(random_style.prefix)
        self.assertIsNotNone(random_style.suffix)

    @patch('page2prompt.api.style_management.StyleManager.add_style')
    def test_generate_random_style(self, mock_add_style):
        message, styles = self.style_manager.generate_random_style()
        self.assertIn("Generated new style:", message)
        mock_add_style.assert_called_once()

if __name__ == '__main__':
    unittest.main()
