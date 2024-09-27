from typing import List, Dict, Optional
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
        required_columns = ["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Reorder columns to match the required order
        df = df[required_columns]
        
        # Reset shot numbers for each scene
        if not df.empty:
            shot_number = 1
            current_scene = df.iloc[0]["Scene"]
            for i, row in df.iterrows():
                if row["Scene"] != current_scene:
                    shot_number = 1
                    current_scene = row["Scene"]
                df.at[i, "Shot"] = shot_number
                shot_number += 1
        
        # Convert all columns to strings to ensure compatibility with gr.DataFrame
        df = df.astype(str)
    
        return df

    def save_proposed_shot_list(self, file_path: str):
        # Always save the full shot list, regardless of the current view
        self.proposed_shot_list.to_csv(file_path, index=False)

    def extract_unique_names(self, shot_list: pd.DataFrame) -> List[str]:
        people = shot_list['People'].dropna().str.split(',').explode().str.strip()
        return list(set(people))

    def extract_unique_places(self, shot_list: pd.DataFrame) -> List[str]:
        places = shot_list['Places'].dropna().str.split(',').explode().str.strip()
        return list(set(places))

    def ensure_all_names_and_places_included(self, subjects_df: pd.DataFrame, unique_names: List[str], unique_places: List[str]) -> pd.DataFrame:
        existing_names = set(subjects_df[subjects_df['Type'] == 'person']['Name'])
        missing_names = set(unique_names) - existing_names
        
        for name in missing_names:
            subjects_df = pd.concat([subjects_df, pd.DataFrame({
                'Name': [name],
                'Description': ['Character mentioned in the shot list'],
                'Type': ['person']
            })], ignore_index=True)
        
        existing_places = set(subjects_df[subjects_df['Type'] == 'place']['Name'])
        missing_places = set(unique_places) - existing_places
        
        for place in missing_places:
            subjects_df = pd.concat([subjects_df, pd.DataFrame({
                'Name': [place],
                'Description': ['Location mentioned in the shot list'],
                'Type': ['place']
            })], ignore_index=True)
        
        return subjects_df

    async def extract_proposed_subjects(self, full_script: str, shot_list: Optional[pd.DataFrame] = None) -> Dict[str, pd.DataFrame]:
        logger.info("Starting subject extraction process in ScriptManager")
        try:
            if shot_list is None:
                shot_list = await self.generate_proposed_shot_list(full_script)
        
            # Validate shot_list DataFrame
            required_columns = ['People', 'Places']
            missing_columns = [col for col in required_columns if col not in shot_list.columns]
        
            if missing_columns:
                logger.warning(f"Shot list is missing columns: {missing_columns}. Adding empty columns.")
                for col in missing_columns:
                    shot_list[col] = ""
        
            # Extract unique people and places
            people = set(shot_list['People'].str.split(',').explode().str.strip().unique())
            places = set(shot_list['Places'].str.split(',').explode().str.strip().unique())
        
            # Create subjects list
            subjects = [{"name": name, "type": "person", "description": ""} for name in people if name and name != 'N/A']
            subjects += [{"name": place, "type": "place", "description": ""} for place in places if place and place != 'N/A']
        
            # Use LLM to generate descriptions (you can keep this part from your existing code)
            # ...
        
            if not subjects:
                logger.warning("No subjects extracted")
                return {"subjects": pd.DataFrame(columns=["name", "description", "type"])}
        
            subjects_df = pd.DataFrame(subjects)
        
            logger.info(f"Successfully created subjects DataFrame with {len(subjects_df)} entries")
        
            # Ensure all required columns exist and are in the correct order
            for col in ["name", "description", "type"]:
                if col not in subjects_df.columns:
                    subjects_df[col] = ""
        
            return {"subjects": subjects_df[['name', 'description', 'type']]}
        except Exception as e:
            logger.exception(f"Error extracting subjects: {str(e)}")
            return {"subjects": pd.DataFrame(columns=["name", "description", "type"])}

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

    def merge_subjects(self, existing_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
        # Combine existing and new dataframes
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates based on 'Name' and keep the last occurrence
        combined_df = combined_df.drop_duplicates(subset='Name', keep='last')
        
        # Reset the index
        combined_df = combined_df.reset_index(drop=True)
        
        return combined_df
    def send_to_subject_management(self, df: pd.DataFrame):
        # This method will overwrite the subject management dataframe with the proposed subjects
        self.subject_manager.set_subjects(df)
        return "Proposed subjects sent to Subject Management"

    def export_proposed_subjects(self, df: pd.DataFrame, file_path: str):
        df.to_csv(file_path, index=False)
        return f"Proposed subjects exported to {file_path}"
