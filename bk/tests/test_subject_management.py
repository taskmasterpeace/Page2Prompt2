import unittest
from unittest.mock import patch, mock_open
import pandas as pd
from page2prompt.api.subject_management import SubjectManager
from page2prompt.models.subject import Subject

class TestSubjectManager(unittest.TestCase):
    def setUp(self):
        self.subject_manager = SubjectManager("test_subjects.csv")

    def test_initial_state(self):
        self.assertEqual(len(self.subject_manager.subjects), 0)

    @patch('page2prompt.api.subject_management.read_csv_file')
    def test_update_subjects(self, mock_read_csv):
        mock_data = [
            {"Name": "Test Subject", "Description": "Test Description", "Alias": "Test Alias", "Type": "person", "Prefix": "Test Prefix", "Suffix": "Test Suffix", "Active": "True"}
        ]
        mock_read_csv.return_value = mock_data
        
        # Simulate the "update" action
        self.subject_manager.update_subjects()
        
        self.assertEqual(len(self.subject_manager.subjects), 1)
        subject = self.subject_manager.subjects[0]
        self.assertEqual(subject.name, "Test Subject")
        self.assertEqual(subject.description, "Test Description")
        self.assertEqual(subject.alias, "Test Alias")
        self.assertEqual(subject.type, "person")
        self.assertEqual(subject.prefix, "Test Prefix")
        self.assertEqual(subject.suffix, "Test Suffix")
        self.assertTrue(subject.active)

    @patch('page2prompt.api.subject_management.read_csv_file')
    @patch('page2prompt.api.subject_management.write_csv_file')
    def test_import_subjects(self, mock_write_csv, mock_read_csv):
        mock_read_csv.return_value = [
            {"name": "Imported Subject", "description": "Imported Description", "alias": "Imported Alias", "type": "person", "prefix": "", "suffix": "", "active": "True"}
        ]
        self.subject_manager.import_subjects("imported_subjects.csv")
        self.assertEqual(len(self.subject_manager.subjects), 1)
        self.assertEqual(self.subject_manager.subjects[0].name, "Imported Subject")
        mock_write_csv.assert_called_once()

    def test_merge_subjects(self):
        existing_df = pd.DataFrame([
            {"Name": "Subject1", "Description": "Description1", "Alias": "Alias1", "Type": "person", "Prefix": "", "Suffix": "", "Active": True},
            {"Name": "Subject2", "Description": "Description2", "Alias": "Alias2", "Type": "place", "Prefix": "", "Suffix": "", "Active": True}
        ])
        new_df = pd.DataFrame([
            {"Name": "Subject2", "Description": "Updated Description", "Alias": "Updated Alias", "Type": "place", "Prefix": "", "Suffix": "", "Active": True},
            {"Name": "Subject3", "Description": "Description3", "Alias": "Alias3", "Type": "prop", "Prefix": "", "Suffix": "", "Active": True}
        ])
        merged_df = self.subject_manager.merge_subjects(existing_df, new_df)
        self.assertEqual(len(merged_df), 3)
        self.assertEqual(merged_df.loc[merged_df['Name'] == 'Subject2', 'Description'].iloc[0], "Updated Description")

if __name__ == '__main__':
    unittest.main()
