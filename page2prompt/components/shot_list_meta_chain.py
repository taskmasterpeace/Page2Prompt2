from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import pandas as pd
from typing import List, Dict, Optional, Tuple
import asyncio

class ShotListMetaChain:
    def __init__(self, api_key: str, subject_manager, style_manager, director_assistant):
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key=api_key)
        self.subject_manager = subject_manager
        self.style_manager = style_manager
        self.director_assistant = director_assistant

    async def generate_bulk_directors_notes(self, script: str, shot_list_df: pd.DataFrame, visual_style: str, director_style_name: str, progress_callback=None) -> pd.DataFrame:
        director_style = self.director_assistant.get_director_style(director_style_name)
        visual_style_desc = self.style_manager.get_full_style_description(visual_style)
        
        total_shots = len(shot_list_df)
        for index, row in shot_list_df.iterrows():
            script_excerpt = row.get('Script Reference', '')
            subjects = self.subject_manager.get_subjects_for_shot(row.get('People', ''))
            notes = await self.generate_directors_notes(
                script_excerpt, 
                row.get('Shot Description', ''), 
                visual_style_desc,
                director_style['notes'], 
                subjects,
                row.get('Scene', ''),
                row.get('Shot', ''),
                row.get('Shot Size', ''),
                ''  # Location is not present in the DataFrame
            )
            shot_list_df.at[index, 'Director\'s Notes'] = notes
            if progress_callback:
                progress_callback((index + 1) / total_shots)
            await asyncio.sleep(0)  # Allow other tasks to run

        # Add 'Setting' column if it doesn't exist
        if 'Setting' not in shot_list_df.columns:
            shot_list_df['Setting'] = ''

        return shot_list_df

    async def generate_directors_notes(self, script_excerpt: str, shot_description: str, visual_style: str, director_style: str, subjects: str, scene: str, shot: str, shot_size: str, location: str) -> str:
        prompt = self._get_directors_notes_prompt()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(
            script_excerpt=script_excerpt,
            shot_description=shot_description,
            visual_style=visual_style,
            director_style=director_style,
            subjects=subjects,
            scene=scene,
            shot=shot,
            shot_size=shot_size,
            location=location
        )
        return response.strip()

    def _get_directors_notes_prompt(self) -> PromptTemplate:
        template = """
        As an experienced film director, provide detailed notes for the following shot, considering all the provided information. Keep in mind the overall visual style of the film, but don't explicitly mention it in your notes.

        Visual Style of the Film: {visual_style}
        Scene: {scene}
        Shot: {shot}
        Shot Size: {shot_size}
        Location: {location}
        Script Excerpt: {script_excerpt}
        Shot Description: {shot_description}
        Director's Style: {director_style}
        Subjects: {subjects}

        Director's Notes:
        """
        return PromptTemplate(template=template, input_variables=["visual_style", "scene", "shot", "shot_size", "location", "script_excerpt", "shot_description", "director_style", "subjects"])

    async def generate_bulk_prompts(self, shot_list_df: pd.DataFrame, visual_style: str, progress_callback=None) -> pd.DataFrame:
        visual_style_prefix, visual_style_suffix = self.style_manager.get_style_prefix_suffix(visual_style)
        total_shots = len(shot_list_df)
        for index, row in shot_list_df.iterrows():
            prompts = await self.generate_prompts(
                row['Script Reference'],
                row['Shot Description'],
                row['Director\'s Notes'],
                visual_style_prefix,
                visual_style_suffix,
                row['Shot Size'],
                row['People']
            )
            shot_list_df.at[index, 'Concise Prompt'] = prompts['concise']
            shot_list_df.at[index, 'Medium Prompt'] = prompts['medium']
            shot_list_df.at[index, 'Detailed Prompt'] = prompts['detailed']
            if progress_callback:
                progress_callback((index + 1) / total_shots)
            await asyncio.sleep(0)  # Allow other tasks to run

        return shot_list_df

    async def generate_prompts(self, script_reference: str, shot_description: str, directors_notes: str, 
                               visual_style_prefix: str, visual_style_suffix: str, shot_size: str, people: str) -> Dict[str, str]:
        prompt = self._get_prompt_generation_template()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(
            script_reference=script_reference,
            shot_description=shot_description,
            directors_notes=directors_notes,
            shot_size=shot_size,
            people=people
        )
        # Parse the response to extract concise, medium, and detailed prompts
        prompts = self._parse_prompt_response(response)
        
        # Add visual style prefix and suffix to each prompt
        for key in prompts:
            prompts[key] = f"{visual_style_prefix} {prompts[key]} {visual_style_suffix}".strip()
        
        return prompts

    def _get_prompt_generation_template(self) -> PromptTemplate:
        template = """
        Generate three versions of a prompt (concise, medium, and detailed) for an image generation AI based on the following information:

        Script Reference: {script_reference}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Shot Size: {shot_size}
        People: {people}

        The prompts should capture the essence of the shot and the director's vision. Do not include the visual style in your generated prompts.

        Concise Prompt:
        Medium Prompt:
        Detailed Prompt:
        """
        return PromptTemplate(template=template, input_variables=["script_reference", "shot_description", "directors_notes", "shot_size", "people"])

    def _parse_prompt_response(self, response: str) -> Dict[str, str]:
        lines = response.strip().split('\n')
        prompts = {}
        current_prompt = None
        for line in lines:
            if line.startswith('Concise Prompt:'):
                current_prompt = 'concise'
                prompts[current_prompt] = ''
            elif line.startswith('Medium Prompt:'):
                current_prompt = 'medium'
                prompts[current_prompt] = ''
            elif line.startswith('Detailed Prompt:'):
                current_prompt = 'detailed'
                prompts[current_prompt] = ''
            elif current_prompt:
                prompts[current_prompt] += line.strip() + ' '
        return {k: v.strip() for k, v in prompts.items()}
