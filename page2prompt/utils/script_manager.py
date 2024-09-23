from typing import List, Dict
import pandas as pd
from .meta_chain import MetaChain

class ScriptManager:
    def __init__(self, meta_chain: MetaChain):
        self.meta_chain = meta_chain
        self.shot_list = pd.DataFrame(columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])

    async def generate_shot_list(self, full_script: str) -> pd.DataFrame:
        prompt = f"""
        Given the following script, generate a detailed shot list. 
        Each shot should include:
        1. Timestamp (use placeholder values like 00:00:00 for now)
        2. Scene number
        3. Shot number
        4. A brief script reference
        5. A detailed shot description
        6. Shot size (e.g., Close-up, Medium Shot, Wide Shot)
        7. People in the shot
        8. Places or locations in the shot

        Script:
        {full_script}

        Provide the shot list in a format that can be easily converted to a CSV, with each field separated by a pipe (|) character.
        """

        response = await self.meta_chain.generate_prompt(prompt)
        
        # Process the response and convert it to a DataFrame
        shots = [shot.split('|') for shot in response.split('\n') if shot.strip()]
        self.shot_list = pd.DataFrame(shots, columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])
        
        return self.shot_list

    def save_shot_list(self, file_path: str):
        self.shot_list.to_csv(file_path, index=False)
