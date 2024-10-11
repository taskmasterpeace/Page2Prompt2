import csv
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple

class Subject:
    def __init__(self, name: str, description: str, alias: str, type: str, prefix: str = "", suffix: str = "", active: bool = True):
        self.name = name
        self.description = description
        self.alias = alias
        self.type = type  # "person", "place", or "prop"
        self.prefix = prefix
        self.suffix = suffix
        self.active = active

import logging

logger = logging.getLogger(__name__)

class SubjectManager:
    def __init__(self, subjects_file: str):
        self.subjects_file = subjects_file
        self.subjects: List[Subject] = self._load_subjects()
        logger.debug(f"Loaded {len(self.subjects)} subjects")

    def _load_subjects(self) -> List[Subject]:
        """Loads subjects from the CSV file."""
        subjects = []
        try:
            logger.debug(f"Attempting to load subjects from {self.subjects_file}")
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
            # Create the file if it doesn't exist
            os.makedirs(os.path.dirname(self.subjects_file), exist_ok=True)
            with open(self.subjects_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])
                writer.writeheader()
        return subjects

    def get_subjects(self) -> List[Subject]:
        """Returns the list of all subjects."""
        return self.subjects

    def get_active_subjects(self) -> List[Subject]:
        """Returns a list of active subjects."""
        return [s for s in self.subjects if s.active]

    def get_people(self) -> List[str]:
        """Returns a list of names of subjects with type 'person'."""
        return [s.name for s in self.subjects if s.type and s.type.lower() == 'person']

    def get_places(self) -> List[str]:
        """Returns a list of names of subjects with type 'place'."""
        return [s.name for s in self.subjects if s.type and s.type.lower() == 'place']

    def get_props(self) -> List[str]:
        """Returns a list of names of subjects with type 'prop'."""
        return [s.name for s in self.subjects if s.type and s.type.lower() == 'prop']

    def get_subject_details(self, name: str) -> Dict:
        """Returns the details of a subject by name."""
        for subject in self.subjects:
            if subject.name == name:
                return vars(subject)
        return {}

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

    def get_subjects_for_shot(self, people: str) -> str:
        active_subjects = self.get_active_subjects()
        shot_subjects = [p.strip() for p in people.split(',')] if people else []
        return ", ".join([s.name for s in active_subjects if s.name in shot_subjects])

    def get_subjects_dataframe(self) -> pd.DataFrame:
        """Returns the subjects as a pandas DataFrame."""
        return pd.DataFrame([vars(s) for s in self.subjects])

    def apply_alias(self, text: str) -> str:
        """Replaces subject names with their aliases in the given text."""
        for subject in self.get_active_subjects():
            if subject.name in text:
                prefix_suffix = f"{subject.prefix} {subject.suffix}".strip()
                if prefix_suffix:
                    text = text.replace(f"{prefix_suffix} {subject.name}", f"{prefix_suffix} {subject.alias}")
                else:
                    text = text.replace(subject.name, subject.alias)
        return text

    def get_subject_prefix_suffix(self, active_subjects: List[str]) -> Tuple[str, str]:
        """Returns the combined prefix and suffix for all active subjects."""
        prefixes = []
        suffixes = []
        for subject in self.get_active_subjects():
            if subject.name in active_subjects:
                if subject.prefix:
                    prefixes.append(subject.prefix)
                if subject.suffix:
                    suffixes.append(subject.suffix)
        return " ".join(prefixes), " ".join(suffixes)

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

    def set_subjects(self, subjects_df: pd.DataFrame):
        self.subjects = []
        for _, row in subjects_df.iterrows():
            subject = Subject(
                name=row['Name'],
                description=row['Description'],
                alias=row['Alias'],
                type=row['Type'],
                prefix=row.get('Prefix', ''),
                suffix=row.get('Suffix', ''),
                active=row.get('Active', True)
            )
            self.subjects.append(subject)
        self._save_subjects()

    def get_all_subjects(self) -> List[Subject]:
        return self.subjects

    def get_name_alias_dict(self) -> Dict[str, str]:
        return {subject.name: subject.alias for subject in self.subjects if subject.alias != subject.name}
