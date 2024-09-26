from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import pandas as pd
from typing import List, Dict, Optional
import asyncio

class ShotListMetaChain:
    def __init__(self, api_key: str, subject_manager, style_manager, director_assistant):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key=api_key)
        self.subject_manager = subject_manager
        self.style_manager = style_manager
        self.director_assistant = director_assistant

    async def generate_bulk_directors_notes(self, script: str, shot_list_df: pd.DataFrame, style_name: str, director_style_name: str, progress_callback=None) -> pd.DataFrame:
        results = []
        visual_style = self.style_manager.get_style(style_name)
        director_style = self.director_assistant.get_director_style(director_style_name)

        total_shots = len(shot_list_df)
        for index, row in shot_list_df.iterrows():
            script_excerpt = script[row['Script Start']:row['Script End']]
            subjects = self._get_subjects_for_shot(row)
            notes = await self.generate_directors_notes(
                script_excerpt, 
                row['Shot Description'], 
                visual_style, 
                director_style, 
                subjects,
                row['Scene'],
                row['Shot'],
                row['Shot Size'],
                row.get('Location', '')
            )
            results.append({
                'Scene': row['Scene'],
                'Shot': row['Shot'],
                'Shot Size': row['Shot Size'],
                'Location': row.get('Location', ''),
                'Director\'s Notes': notes,
                'Subjects': ", ".join(subjects)
            })
            if progress_callback:
                progress_callback((index + 1) / total_shots)
            await asyncio.sleep(0)  # Allow other tasks to run

        return pd.DataFrame(results)

    async def generate_directors_notes(self, script_excerpt: str, shot_description: str, visual_style: Dict[str, str], director_style: Dict[str, str], subjects: List[str], scene: str, shot: str, shot_size: str, location: str) -> str:
        prompt = self._get_directors_notes_prompt()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(
            script_excerpt=script_excerpt,
            shot_description=shot_description,
            visual_style=f"{visual_style['prefix']} {visual_style['suffix']}".strip(),
            director_style=director_style['notes'],
            subjects=", ".join(subjects),
            scene=scene,
            shot=shot,
            shot_size=shot_size,
            location=location
        )
        return response.strip()

    def _get_subjects_for_shot(self, row: pd.Series) -> List[str]:
        all_subjects = self.subject_manager.get_active_subjects()
        shot_subjects = []
        if 'People' in row and row['People']:
            shot_subjects.extend([p.strip() for p in row['People'].split(',')])
        if 'Places' in row and row['Places']:
            shot_subjects.extend([p.strip() for p in row['Places'].split(',')])
        return [subject for subject in shot_subjects if subject in [s.name for s in all_subjects]]

    def _get_directors_notes_prompt(self) -> PromptTemplate:
        template = """
        As an experienced film director, provide detailed notes for the following shot, considering all the provided information.

        Scene: {scene}
        Shot: {shot}
        Shot Size: {shot_size}
        Location: {location}
        Script Excerpt: {script_excerpt}
        Shot Description: {shot_description}
        Visual Style: {visual_style}
        Director's Style: {director_style}
        Subjects: {subjects}

        Director's Notes:
        """
        return PromptTemplate(template=template, input_variables=["scene", "shot", "shot_size", "location", "script_excerpt", "shot_description", "visual_style", "director_style", "subjects"])
