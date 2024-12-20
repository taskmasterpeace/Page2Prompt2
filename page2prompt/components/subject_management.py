import csv
import pandas as pd
from typing import Dict, List

class SubjectManager:
    def __init__(self, subjects_file: str = "subjects.csv"):
        self.subjects_file = subjects_file
        self.subjects = self._load_subjects()

    def _load_subjects(self) -> List[Dict]:
        """Loads subjects from the CSV file."""
        subjects = []
        try:
            with open(self.subjects_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    subjects.append(row)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["Name", "Category", "Description", "Alias", "Inventory", "Project", "Active"])
                writer.writeheader()
        return subjects

    def get_subjects(self) -> List[Dict]:
        """Returns the list of subjects."""
        return self.subjects

    def get_active_subjects(self) -> List[Dict]:
        """Returns a list of active subjects."""
        return [s for s in self.subjects if s.get("Active", "False").lower() == "true"]

    def add_subject(self, subject_data: Dict) -> None:
        """Adds a new subject to the list and saves to the CSV file."""
        self.subjects.append(subject_data)
        self._save_subjects()

    def update_subject(self, subject_data: Dict) -> None:
        """Updates an existing subject in the list and saves to the CSV file."""
        for i, subject in enumerate(self.subjects):
            if subject["Name"] == subject_data["Name"]:
                self.subjects[i] = subject_data
                break
        self._save_subjects()

    def delete_subject(self, subject_name: str) -> None:
        """Deletes a subject from the list and saves to the CSV file."""
        self.subjects = [s for s in self.subjects if s["Name"] != subject_name]
        self._save_subjects()

    def _save_subjects(self) -> None:
        """Saves the subjects to the CSV file."""
        with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Name", "Category", "Description", "Alias", "Inventory", "Project", "Active"])
            writer.writeheader()
            writer.writerows(self.subjects)
import csv
from typing import Dict, List

class SubjectManager:
    def __init__(self, subjects_file: str = "subjects.csv"):
        self.subjects_file = subjects_file
        self.subjects = self._load_subjects()

    def _load_subjects(self) -> List[Dict]:
        """Loads subjects from the CSV file."""
        subjects = []
        try:
            with open(self.subjects_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['Active'] = row.get('Active', 'False').lower() == 'true'
                    subjects.append(row)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["Name", "Category", "Description", "Alias", "Inventory", "Project", "Active"])
                writer.writeheader()
        return subjects

    def get_subjects(self) -> List[Dict]:
        """Returns the list of subjects."""
        return self.subjects

    def get_active_subjects(self) -> List[Dict]:
        """Returns a list of active subjects."""
        return [s for s in self.subjects if s.get("Active", False)]

    def add_subject(self, subject_data: Dict) -> None:
        """Adds a new subject to the list and saves to the CSV file."""
        subject_data['Active'] = subject_data.get('Active', False)
        self.subjects.append(subject_data)
        self._save_subjects()

    def update_subject(self, subject_data: Dict) -> None:
        """Updates an existing subject in the list and saves to the CSV file."""
        for i, subject in enumerate(self.subjects):
            if subject["Name"] == subject_data["Name"]:
                subject_data['Active'] = subject_data.get('Active', False)
                self.subjects[i] = subject_data
                break
        self._save_subjects()

    def delete_subject(self, subject_name: str) -> None:
        """Deletes a subject from the list and saves to the CSV file."""
        self.subjects = [s for s in self.subjects if s["Name"] != subject_name]
        self._save_subjects()

    def _save_subjects(self) -> None:
        """Saves the subjects to the CSV file."""
        with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Name", "Category", "Description", "Alias", "Inventory", "Project", "Active"])
            writer.writeheader()
            for subject in self.subjects:
                subject['Active'] = str(subject.get('Active', False))
            writer.writerows(self.subjects)

    def merge_subjects(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """Merges existing subjects with new subjects."""
        # Combine existing and new dataframes
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates based on 'Name' and keep the last occurrence
        combined_df = combined_df.drop_duplicates(subset='Name', keep='last')
        
        # Reset the index
        combined_df = combined_df.reset_index(drop=True)
        
        return combined_df

    def get_subjects_dataframe(self) -> pd.DataFrame:
        """Returns the subjects as a DataFrame."""
        return pd.DataFrame(self.subjects)

    def set_subjects(self, subjects_df: pd.DataFrame):
        """Sets the subjects from a DataFrame."""
        self.subjects = subjects_df.to_dict('records')
        self._save_subjects()
