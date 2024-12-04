from typing import List, Optional
from page2prompt.models.subject import Subject
from page2prompt.utils.helpers import read_csv_file, write_csv_file

class SubjectManager:
    def __init__(self, subjects_file: str):
        self.subjects_file = subjects_file
        self.subjects: List[Subject] = self._load_subjects()

    def _load_subjects(self) -> List[Subject]:
        try:
            subjects_data = read_csv_file(self.subjects_file)
            return [Subject.from_dict(subject) for subject in subjects_data]
        except FileNotFoundError:
            print(f"Subjects file not found: {self.subjects_file}")
            return []
        except Exception as e:
            print(f"Error loading subjects: {str(e)}")
            return []

    def get_subjects(self) -> List[Subject]:
        return self.subjects

    def get_subject(self, name: str) -> Optional[Subject]:
        for subject in self.subjects:
            if subject.name == name:
                return subject
        return None

    def add_subject(self, subject: Subject) -> None:
        if not any(s.name == subject.name for s in self.subjects):
            self.subjects.append(subject)
            self._save_subjects()

    def update_subject(self, subject: Subject) -> None:
        for i, s in enumerate(self.subjects):
            if s.name == subject.name:
                self.subjects[i] = subject
                self._save_subjects()
                return

    def delete_subject(self, name: str) -> None:
        self.subjects = [s for s in self.subjects if s.name != name]
        self._save_subjects()

    def _save_subjects(self) -> None:
        subjects_data = [subject.to_dict() for subject in self.subjects]
        write_csv_file(self.subjects_file, subjects_data, fieldnames=["name", "description", "alias", "type", "prefix", "suffix", "active"])
