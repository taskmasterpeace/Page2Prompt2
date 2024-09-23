from typing import List, Dict
import pandas as pd
from ..components.meta_chain import MetaChain

class ScriptManager:
    def __init__(self, meta_chain: MetaChain):
        self.meta_chain = meta_chain
        self.shot_list = pd.DataFrame(columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        self.proposed_subjects = pd.DataFrame(columns=["Name", "Description", "Type"])

    async def generate_proposed_shot_list(self, full_script: str, view_option: str) -> pd.DataFrame:
        response = await self.meta_chain.generate_proposed_shot_list(full_script)
        
        # Process the response and convert it to a DataFrame
        shots = [shot.split('|') for shot in response.split('\n') if shot.strip()]
        self.proposed_shot_list = pd.DataFrame(shots, columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        
        # Apply the view option
        if view_option == "Simple View":
            return self.proposed_shot_list[["Scene", "Shot Description", "Shot Size", "People"]]
        else:  # Detailed View
            return self.proposed_shot_list

    def save_proposed_shot_list(self, file_path: str):
        # Always save the full shot list, regardless of the current view
        self.proposed_shot_list.to_csv(file_path, index=False)

    async def extract_proposed_subjects(self, full_script: str) -> pd.DataFrame:
        response = await self.meta_chain.extract_proposed_subjects(full_script, self.proposed_shot_list)
        
        # Process the response and convert it to a DataFrame
        subjects = [subject.split('|') for subject in response.split('\n') if subject.strip()]
        self.proposed_subjects = pd.DataFrame(subjects, columns=["Name", "Description", "Type"])
        return self.proposed_subjects

    def update_proposed_subject(self, selected_rows, name: str, description: str, subject_type: str):
        if len(selected_rows) > 0:
            index = selected_rows[0]
            self.proposed_subjects.loc[index] = [name, description, subject_type]
        return self.proposed_subjects

    def add_proposed_subject(self, name: str, description: str, subject_type: str):
        new_subject = pd.DataFrame([[name, description, subject_type]], columns=["Name", "Description", "Type"])
        self.proposed_subjects = pd.concat([self.proposed_subjects, new_subject], ignore_index=True)

    def delete_proposed_subject(self, index: int):
        self.proposed_subjects = self.proposed_subjects.drop(index).reset_index(drop=True)

    def get_proposed_subjects(self) -> pd.DataFrame:
        return self.proposed_subjects

    def send_to_subject_management(self):
        # This method will overwrite the subject management dataframe with the proposed subjects
        self.subject_manager.set_subjects(self.proposed_subjects)

    def execute_extraction(self):
        # This method will trigger the actual extraction process
        # For now, it's just a placeholder
        return self.proposed_subjects

    def export_proposed_subjects(self, file_path: str):
        self.proposed_subjects.to_csv(file_path, index=False)
