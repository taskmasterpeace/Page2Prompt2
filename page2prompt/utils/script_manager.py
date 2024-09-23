from typing import List, Dict
import pandas as pd
from ..components.meta_chain import MetaChain

class ScriptManager:
    def __init__(self, meta_chain: MetaChain):
        self.meta_chain = meta_chain
        self.shot_list = pd.DataFrame(columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])

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