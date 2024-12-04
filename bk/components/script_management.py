import pandas as pd
from typing import Dict, Any, List
from page2prompt.api.shot_list_generation import ShotListGenerator

class ScriptManager:
    def __init__(self):
        self.script = ""
        self.proposed_subjects = pd.DataFrame(columns=['Name', 'Type', 'Description'])

    def set_script(self, script: str):
        self.script = script

    def get_script(self) -> str:
        return self.script

    def get_proposed_subjects(self) -> pd.DataFrame:
        return self.proposed_subjects

    def add_proposed_subject(self, name: str, subject_type: str, description: str):
        new_subject = pd.DataFrame({'Name': [name], 'Type': [subject_type], 'Description': [description]})
        self.proposed_subjects = pd.concat([self.proposed_subjects, new_subject], ignore_index=True)

    def clear_proposed_subjects(self):
        self.proposed_subjects = pd.DataFrame(columns=['Name', 'Type', 'Description'])

    async def generate_proposed_shot_list(self, api_key, subject_manager, style_manager, director_assistant) -> pd.DataFrame:
        shot_list_generator = ShotListGenerator(api_key, subject_manager, style_manager, director_assistant)
        shots = await shot_list_generator.generate_shot_list(self.script)
        return pd.DataFrame([shot.to_dict() for shot in shots])

    async def extract_proposed_subjects(self, shot_list: pd.DataFrame) -> Dict[str, Any]:
        # Implement the subject extraction logic here
        # This could involve analyzing the shot list and the script
        pass

    def merge_subjects(self, current_df: pd.DataFrame, new_subjects: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([current_df, new_subjects]).drop_duplicates(subset=['Name'], keep='last').reset_index(drop=True)

    def export_proposed_subjects(self, subjects_df: pd.DataFrame, filename: str) -> str:
        subjects_df.to_csv(filename, index=False)
        return f"Subjects exported to {filename}"
