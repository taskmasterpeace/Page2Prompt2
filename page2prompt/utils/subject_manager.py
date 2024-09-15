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
