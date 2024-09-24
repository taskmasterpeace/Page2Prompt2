from typing import List, Dict
import pandas as pd
import json
import logging
from ..components.meta_chain import MetaChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptManager:
    def __init__(self, meta_chain: MetaChain):
        self.meta_chain = meta_chain
        self.shot_list = pd.DataFrame(columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        self.proposed_subjects = pd.DataFrame(columns=["Name", "Description", "Type"])

    def parse_llm_output(self, llm_output: str) -> pd.DataFrame:
        rows = [row.split('|') for row in llm_output.strip().split('\n')]
        df = pd.DataFrame(rows, columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        return df

    async def generate_proposed_shot_list(self, full_script: str) -> pd.DataFrame:
        response = await self.meta_chain.generate_proposed_shot_list(full_script)
        
        if isinstance(response, str):
            df = self.parse_llm_output(response)
        elif isinstance(response, pd.DataFrame):
            df = response
        else:
            raise ValueError("Unexpected response type from MetaChain")
        
        # Ensure all required columns exist and are in the correct order
        required_columns = ["Timestamp", "Scene", "Shot", "Reference", "Shot Description", "Shot Size", "People", "Places"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Reorder columns to match the required order
        df = df[required_columns]
        
        # Reset shot numbers for each scene
        def reset_shot_numbers(df):
            shot_number = 1
            current_scene = df.iloc[0]["Scene"]
            for i, row in df.iterrows():
                if row["Scene"] != current_scene:
                    shot_number = 1
                    current_scene = row["Scene"]
                df.at[i, "Shot"] = shot_number
                shot_number += 1
            return df

        # Apply the reset_shot_numbers function
        df = reset_shot_numbers(df)
    
        # Convert all columns to strings to ensure compatibility with gr.DataFrame
        df = df.astype(str)
    
        return df

    def save_proposed_shot_list(self, file_path: str):
        # Always save the full shot list, regardless of the current view
        self.proposed_shot_list.to_csv(file_path, index=False)

    async def extract_proposed_subjects(self, full_script: str) -> pd.DataFrame:
        try:
            subjects_dict = await self.meta_chain.extract_proposed_subjects(full_script)
            subjects_json = json.loads(subjects_dict)
            subjects_df = pd.DataFrame(subjects_json['subjects'])
            return subjects_df
        except Exception as e:
            print(f"Error extracting subjects: {str(e)}")
            return pd.DataFrame(columns=["name", "description", "type"])

    def approve_proposed_subjects(self):
        # Create a set of all unique people from the shot list
        all_people = set()
        for _, row in self.shot_list.iterrows():
            people = [person.strip() for person in row['People'].split(',') if person.strip()]
            all_people.update(people)
        
        # Add all subjects from the shot list to the proposed subjects
        for person in all_people:
            if person not in self.proposed_subjects['Name'].values:
                self.proposed_subjects = pd.concat([self.proposed_subjects, pd.DataFrame({
                    'Name': [person],
                    'Description': ['Description pending based on script analysis.'],
                    'Type': ['person']
                })], ignore_index=True)
        
        return self.proposed_subjects

    def update_proposed_subject(self, df: pd.DataFrame, name: str, description: str, subject_type: str):
        selected_index = df.index[df['Name'] == name].tolist()
        if selected_index:
            index = selected_index[0]
            self.proposed_subjects.loc[index] = [name, description, subject_type]
        else:
            # If the subject doesn't exist, add it as a new row
            new_subject = pd.DataFrame([[name, description, subject_type]], columns=["Name", "Description", "Type"])
            self.proposed_subjects = pd.concat([self.proposed_subjects, new_subject], ignore_index=True)
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
    def send_to_subject_management(self, df: pd.DataFrame):
        # This method will overwrite the subject management dataframe with the proposed subjects
        self.subject_manager.set_subjects(df)
        return "Proposed subjects sent to Subject Management"

    def export_proposed_subjects(self, df: pd.DataFrame, file_path: str):
        df.to_csv(file_path, index=False)
        return f"Proposed subjects exported to {file_path}"
