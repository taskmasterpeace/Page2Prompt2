import pandas as pd
import io
from typing import List, Dict
from page2prompt.components.meta_chain import MetaChain

async def generate_shot_list(concept: str, genre: str, descriptors: str, lyrics: str, chat_history: List[List[str]], approved_treatment: str, characters: pd.DataFrame) -> pd.DataFrame:
    meta_chain = MetaChain()
    
    # Combine all inputs into a single prompt
    prompt = f"""
    Project Concept: {concept}
    Approved Video Treatment: {approved_treatment}
    Characters and Wardrobe:
    {characters.to_csv(index=False)}
    Genre: {genre}
    Descriptors: {descriptors}
    Lyrics: {lyrics}
    Conversation History: {chat_history}
    
    As a virtual director, generate a detailed shot list for the music video, including scene numbers, shot descriptions, and any additional notes.
    Ensure that character appearances and wardrobe are reflected in the shot descriptions.
    Format the shot list as a CSV with columns: Scene, Shot, Description, Notes, Camera Angle, Lighting, Pacing, Color Palette.
    """
    
    # Call the LLM to generate the shot list
    shot_list_text = await meta_chain.generate_shot_list(prompt)
    
    # Convert the output into a DataFrame format
    shot_list_df = parse_shot_list(shot_list_text)
    return shot_list_df

def parse_shot_list(shot_list_text: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(io.StringIO(shot_list_text))
        return df
    except Exception as e:
        error_df = pd.DataFrame(
            [["Error parsing shot list", "", "", "", "", "", "", ""]],
            columns=["Scene", "Shot", "Description", "Notes", "Camera Angle", "Lighting", "Pacing", "Color Palette"]
        )
        return error_df
