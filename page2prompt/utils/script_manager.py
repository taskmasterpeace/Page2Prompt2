from typing import List, Dict
import pandas as pd
import json
from ..components.meta_chain import MetaChain

class ScriptManager:
    def __init__(self, meta_chain: MetaChain):
        self.meta_chain = meta_chain
        self.shot_list = pd.DataFrame(columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        self.proposed_subjects = pd.DataFrame(columns=["Name", "Description", "Type"])

    async def generate_proposed_shot_list(self, full_script: str) -> pd.DataFrame:
        response = await self.meta_chain.generate_proposed_shot_list(full_script)
        
        # Process the response and convert it to a DataFrame
        shots = [shot.split('|') for shot in response.split('\n') if shot.strip()]
        df = pd.DataFrame(shots, columns=["Scene", "Shot Description", "Shot Size", "People"])
        
        # Add empty columns for the detailed view
        for col in ["Timestamp", "Shot", "Script Reference", "Places"]:
            if col not in df.columns:
                df[col] = ""
        
        # Ensure "Shot" column is filled
        df["Shot"] = df.index + 1  # Assuming each row is a separate shot
        
        return df

    def save_proposed_shot_list(self, file_path: str):
        # Always save the full shot list, regardless of the current view
        self.proposed_shot_list.to_csv(file_path, index=False)

    async def extract_proposed_subjects(self, full_script: str) -> pd.DataFrame:
        response = await self.meta_chain.extract_proposed_subjects(full_script, self.shot_list)
        
        try:
            data = json.loads(response)
            df = pd.DataFrame(data['subjects'])
            df['Description'] = df['Description'].apply(lambda x: x[:300] if len(x) > 300 else x)  # Limit description to ~2-3 sentences
            self.proposed_subjects = df
            return df
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            return pd.DataFrame()

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
