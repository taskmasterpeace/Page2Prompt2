import pandas as pd
from typing import List, Dict, Any, Optional
from page2prompt.models.shot import Shot
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.callbacks.manager import get_openai_callback

class ShotListGenerator:
    def __init__(self, api_key: str, subject_manager, style_manager, director_assistant):
        self.api_key = api_key
        self.subject_manager = subject_manager
        self.style_manager = style_manager
        self.director_assistant = director_assistant
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0125-preview", openai_api_key=self.api_key)

    async def generate_shot_list(self, script: str) -> List[Shot]:
        prompt = f"""
        Given the following script, generate a proposed detailed shot list. 
        Include the following information for each shot, separated by pipe characters (|):
        1. Timestamp
        2. Scene
        3. Shot
        4. Reference
        5. Shot Description
        6. Shot Size
        7. People
        8. Places

        Script:
        {script}

        Important instructions:
        - Do not include any headers, labels, or titles in the output.
        - Start each new line with the timestamp.
        - Use N/A for any fields that are not applicable or cannot be determined from the script.
        - For the Script Reference, include the exact portion of the script this shot is based on, word-for-word. This should be a direct quote from the script.
        - Scene numbers should change when the script indicates a new scene (e.g., INT. ROOM - DAY).
        - Shot numbers should restart at 1 for each new scene.
        - Ensure that the Shot Description provides more detail than just repeating the Script Reference.

        Please generate the shot list in this format, ensuring that the Reference column contains exact quotes from the provided script.
        """

        try:
            with get_openai_callback() as cb:
                chain = RunnableSequence(
                    PromptTemplate(template=prompt, input_variables=[]),
                    self.llm
                )
                result = await chain.ainvoke({})
        
            content = result.content
            shot_list = self.parse_shot_list(content)
            return [Shot(**shot) for shot in shot_list]
        except Exception as e:
            print(f"Error generating shot list: {str(e)}")
            return []

    async def generate_bulk_directors_notes(self, full_script: str, master_shot_list: pd.DataFrame, style: str, director_style: str, progress_callback=None) -> pd.DataFrame:
        notes_df = master_shot_list.copy()
        notes_df['Director\'s Notes'] = ''

        total_shots = len(notes_df)
        for index, row in notes_df.iterrows():
            if progress_callback:
                progress_callback((index + 1) / total_shots)

            prompt = f"""
            Given the following script excerpt and shot description, generate detailed director's notes.
            Consider the visual style '{style}' and the director's style '{director_style}'.

            Script Excerpt: {row['Script Reference']}
            Shot Description: {row['Shot Description']}
            Shot Size: {row['Shot Size']}
            People: {row['People']}

            Director's Notes:
            """

            try:
                with get_openai_callback() as cb:
                    chain = RunnableSequence(
                        PromptTemplate(template=prompt, input_variables=[]),
                        self.llm
                    )
                    result = await chain.ainvoke({})
                notes_df.at[index, 'Director\'s Notes'] = result.content.strip()
            except Exception as e:
                print(f"Error generating director's notes for shot {index + 1}: {str(e)}")
                notes_df.at[index, 'Director\'s Notes'] = "Error generating notes"

        return notes_df

    def parse_shot_list(self, raw_shot_list: str) -> List[Dict[str, Any]]:
        shots = []
        for line in raw_shot_list.strip().split('\n'):
            parts = line.split('|')
            if len(parts) == 8:
                shot = {
                    "timestamp": parts[0],
                    "scene": parts[1],
                    "shot": parts[2],
                    "reference": parts[3],
                    "description": parts[4],
                    "size": parts[5],
                    "people": parts[6],
                    "places": parts[7]
                }
                shots.append(shot)
        return shots

    async def generate_bulk_prompts(self, shot_list_df: pd.DataFrame, style: str, director_style: str) -> pd.DataFrame:
        prompts_df = shot_list_df.copy()
        prompts_df['Concise Prompt'] = ''
        prompts_df['Medium Prompt'] = ''
        prompts_df['Detailed Prompt'] = ''

        for index, row in prompts_df.iterrows():
            prompt = f"""
            Generate three prompts (concise, medium, and detailed) for the following shot:
            
            Shot Description: {row['Shot Description']}
            Shot Size: {row['Shot Size']}
            People: {row['People']}
            Places: {row['Places']}
            
            Consider the visual style '{style}' and the director's style '{director_style}'.
            
            Prompts:
            """

            try:
                with get_openai_callback() as cb:
                    chain = RunnableSequence(
                        PromptTemplate(template=prompt, input_variables=[]),
                        self.llm
                    )
                    result = await chain.ainvoke({})
                
                prompts = result.content.strip().split('\n\n')
                prompts_df.at[index, 'Concise Prompt'] = prompts[0] if len(prompts) > 0 else ''
                prompts_df.at[index, 'Medium Prompt'] = prompts[1] if len(prompts) > 1 else ''
                prompts_df.at[index, 'Detailed Prompt'] = prompts[2] if len(prompts) > 2 else ''
            except Exception as e:
                print(f"Error generating prompts for shot {index + 1}: {str(e)}")
                prompts_df.at[index, 'Concise Prompt'] = "Error generating prompt"
                prompts_df.at[index, 'Medium Prompt'] = "Error generating prompt"
                prompts_df.at[index, 'Detailed Prompt'] = "Error generating prompt"

        return prompts_df
