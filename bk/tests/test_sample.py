import unittest
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from page2prompt.utils import helpers

class TestSample(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)

    def test_read_csv_file(self):
        self.assertTrue(hasattr(helpers, 'read_csv_file'))

if __name__ == '__main__':
    unittest.main()
