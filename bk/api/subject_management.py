import csv
import os
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from page2prompt.models.subject import Subject
from page2prompt.utils.helpers import read_csv_file, write_csv_file

logger = logging.getLogger(__name__)

class SubjectManager:
    def __init__(self, subjects_file: str = "subjects.csv"):
        self.subjects_file = subjects_file
        self.subjects: List[Subject] = []
        self.update_subjects()

    def update_subjects(self):
        """Loads subjects from the CSV file."""
        self.subjects = self._load_subjects()

    def _load_subjects(self) -> List[Subject]:
        """Loads subjects from the CSV file."""
        try:
            subjects_data = read_csv_file(self.subjects_file)
            return [Subject.from_dict({k.lower(): v for k, v in subject.items()}) for subject in subjects_data]
        except FileNotFoundError:
            logger.warning(f"Subjects file not found. Creating a new file: {self.subjects_file}")
            self._create_empty_subjects_file()
            return []
        except Exception as e:
            logger.error(f"Error loading subjects: {str(e)}")
            return []

    def _create_empty_subjects_file(self):
        os.makedirs(os.path.dirname(self.subjects_file), exist_ok=True)
        write_csv_file(self.subjects_file, [], fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])

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

    def get_subject_details(self, name: str) -> Optional[Dict]:
        """Returns the details of a subject by name."""
        subject = self.get_subject(name)
        return subject.to_dict() if subject else None

    def add_subject(self, subject: Subject) -> None:
        """Adds a new subject to the list and saves to the CSV file."""
        if not any(s.name == subject.name for s in self.subjects):
            self.subjects.append(subject)
            self._save_subjects()
            logger.info(f"Subject '{subject.name}' added successfully")
        else:
            logger.warning(f"Subject '{subject.name}' already exists")

    def update_subject(self, subject: Subject) -> None:
        """Updates an existing subject in the list and saves to the CSV file."""
        for i, s in enumerate(self.subjects):
            if s.name == subject.name:
                self.subjects[i] = subject
                self._save_subjects()
                logger.info(f"Subject '{subject.name}' updated successfully")
                return
        logger.warning(f"Subject '{subject.name}' not found for update")

    def delete_subject(self, name: str) -> None:
        """Deletes a subject from the list and saves to the CSV file."""
        initial_count = len(self.subjects)
        self.subjects = [s for s in self.subjects if s.name != name]
        if len(self.subjects) < initial_count:
            self._save_subjects()
            logger.info(f"Subject '{name}' deleted successfully")
        else:
            logger.warning(f"Subject '{name}' not found for deletion")

    def _save_subjects(self) -> None:
        """Saves the subjects to the CSV file."""
        try:
            subjects_data = [subject.to_dict() for subject in self.subjects]
            write_csv_file(self.subjects_file, subjects_data, fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])
            logger.info("Subjects saved successfully")
        except Exception as e:
            logger.error(f"Error saving subjects: {str(e)}")

    def get_subjects_for_shot(self, people: str) -> str:
        active_subjects = self.get_active_subjects()
        shot_subjects = [p.strip() for p in people.split(',')] if people else []
        return ", ".join([s.name for s in active_subjects if s.name in shot_subjects])

    def get_subjects_dataframe(self) -> pd.DataFrame:
        """Returns the subjects as a pandas DataFrame."""
        return pd.DataFrame([s.to_dict() for s in self.subjects])

    def apply_alias(self, text: str) -> str:
        """Replaces subject names with their aliases in the given text."""
        for subject in self.get_active_subjects():
            if subject.name in text:
                prefix = subject.prefix.strip() + " " if subject.prefix else ""
                suffix = " " + subject.suffix.strip() if subject.suffix else ""
                old_text = f"{prefix}{subject.name}{suffix}"
                new_text = f"{prefix}{subject.alias}{suffix}"
                text = text.replace(old_text, new_text)
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
            imported_subjects = read_csv_file(file_path)
            for row in imported_subjects:
                subject = Subject.from_dict(row)
                self.add_subject(subject)
            logger.info(f"Subjects imported successfully from {file_path}")
        except Exception as e:
            logger.error(f"Error importing subjects: {str(e)}")

    def export_subjects(self, file_path: str) -> None:
        """Exports subjects to a CSV file."""
        try:
            subjects_data = [subject.to_dict() for subject in self.subjects]
            write_csv_file(file_path, subjects_data, fieldnames=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"])
            logger.info(f"Subjects exported successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting subjects: {str(e)}")

    def merge_subjects(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        """Merges existing subjects with new subjects."""
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset='Name', keep='last')
        return combined_df.reset_index(drop=True)

    def set_subjects(self, subjects_df: pd.DataFrame) -> None:
        """Sets the subjects from a DataFrame."""
        self.subjects = [Subject.from_dict(row) for _, row in subjects_df.iterrows()]
        self._save_subjects()
        logger.info("Subjects updated from DataFrame")

    def get_subject(self, name: str) -> Optional[Subject]:
        """Returns a subject by name."""
        for subject in self.subjects:
            if subject.name == name:
                return subject
        logger.warning(f"Subject '{name}' not found")
        return None

    def get_subject_by_alias(self, alias: str) -> Optional[Subject]:
        """Returns a subject by alias."""
        for subject in self.subjects:
            if subject.alias == alias:
                return subject
        logger.warning(f"Subject with alias '{alias}' not found")
        return None
