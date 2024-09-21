import csv
import pandas as pd
from typing import Dict, List, Optional

class Subject:
    def __init__(self, name: str, description: str, alias: str, type: str, prefix: str = "", suffix: str = "", active: bool = True):
        self.name = name
        self.description = description
        self.alias = alias
        self.type = type  # "person", "place", or "prop"
        self.prefix = prefix
        self.suffix = suffix
        self.active = active

class SubjectManager:
    def __init__(self, subjects_file: str = "subjects.csv"):
        self.subjects_file = subjects_file
        self.subjects: List[Subject] = self._load_subjects()

    def _load_subjects(self) -> List[Subject]:
        """Loads subjects from the CSV file."""
        subjects = []
        try:
            with open(self.subjects_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    subjects.append(Subject(
                        name=row['Name'],
                        description=row['Description'],
                        alias=row['Alias'],
                        type=row['Type'],
                        prefix=row.get('Prefix', ''),
                        suffix=row.get('Suffix', ''),
                        active=row.get('Active', 'True').lower() == 'true'
                    ))
        except FileNotFoundError:
            # File doesn't exist, return an empty list
            pass
        return subjects

    def get_subjects(self) -> List[Subject]:
        """Returns the list of all subjects."""
        return self.subjects

    def get_active_subjects(self) -> List[Subject]:
        """Returns a list of active subjects."""
        return [s for s in self.subjects if s.active]

    def add_subject(self, subject: Subject) -> None:
        """Adds a new subject to the list and saves to the CSV file."""
        if not any(s.name == subject.name for s in self.subjects):
            self.subjects.append(subject)
            self._save_subjects()

    def update_subject(self, subject: Subject) -> None:
        """Updates an existing subject in the list and saves to the CSV file."""
        for i, s in enumerate(self.subjects):
            if s.name == subject.name:
                self.subjects[i] = subject
                break
        self._save_subjects()

    def delete_subject(self, name: str) -> None:
        """Deletes a subject from the list and saves to the CSV file."""
        self.subjects = [s for s in self.subjects if s.name != name]
        self._save_subjects()

    def _save_subjects(self) -> None:
        """Saves the subjects to the CSV file."""
        with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])
            writer.writeheader()
            for subject in self.subjects:
                writer.writerow({
                    "Name": subject.name,
                    "Description": subject.description,
                    "Alias": subject.alias,
                    "Type": subject.type,
                    "Prefix": subject.prefix,
                    "Suffix": subject.suffix,
                    "Active": str(subject.active)
                })

    def get_subjects_dataframe(self) -> pd.DataFrame:
        """Returns the subjects as a pandas DataFrame."""
        return pd.DataFrame([vars(s) for s in self.subjects])

    def apply_alias(self, text: str) -> str:
        """Replaces subject names with their aliases in the given text."""
        for subject in self.get_active_subjects():
            text = text.replace(subject.name, subject.alias)
        return text

    def apply_prefix_suffix(self, text: str) -> str:
        """Applies prefix and suffix to subject mentions in the given text."""
        for subject in self.get_active_subjects():
            if subject.name in text:
                text = text.replace(subject.name, f"{subject.prefix} {subject.name} {subject.suffix}".strip())
        return text

    def import_subjects(self, file_path: str) -> None:
        """Imports subjects from a CSV file."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    subject = Subject(
                        name=row['Name'],
                        description=row['Description'],
                        alias=row['Alias'],
                        type=row['Type'],
                        prefix=row.get('Prefix', ''),
                        suffix=row.get('Suffix', ''),
                        active=row.get('Active', 'True').lower() == 'true'
                    )
                    self.add_subject(subject)
        except Exception as e:
            print(f"Error importing subjects: {str(e)}")

    def export_subjects(self, file_path: str) -> None:
        """Exports subjects to a CSV file."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])
                writer.writeheader()
                for subject in self.subjects:
                    writer.writerow({
                        "Name": subject.name,
                        "Description": subject.description,
                        "Alias": subject.alias,
                        "Type": subject.type,
                        "Prefix": subject.prefix,
                        "Suffix": subject.suffix,
                        "Active": str(subject.active)
                    })
        except Exception as e:
            print(f"Error exporting subjects: {str(e)}")
