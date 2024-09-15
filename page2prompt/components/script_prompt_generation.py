import asyncio
from typing import Dict, List, Optional, Tuple
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from utils.style_manager import StyleManager
from components.subject_management import SubjectManager
from components.meta_chain import MetaChain

class ScriptPromptGenerator:
    def __init__(self, style_manager: StyleManager, subject_manager: SubjectManager, meta_chain: MetaChain):
        self.style_manager = style_manager
        self.subject_manager = subject_manager
        self.meta_chain = meta_chain

    async def generate_prompts(
        self,
        script_excerpt: str,
        shot_description: str,
        directors_notes: str,
        style: Optional[str] = None,
        director_style: Optional[str] = None,
        stick_to_script: bool = False,
        highlighted_text: Optional[str] = None,
        full_script: Optional[str] = None,
        end_parameters: Optional[str] = None,
        camera_shot: Optional[str] = None,
        camera_move: Optional[str] = None,
        camera_size: Optional[str] = None,
        framing: Optional[str] = None,
        depth_of_field: Optional[str] = None,
    ) -> Tuple[str, str, str, str, str, str]:

        # 1. Get active subjects
        active_subjects = self.subject_manager.get_active_subjects()

        # 2. Generate prompts using MetaChain
        camera_settings = {
            "camera_shot": camera_shot,
            "camera_move": camera_move,
            "camera_size": camera_size,
            "framing": framing,
            "depth_of_field": depth_of_field
        }
        
        prompts = await self.meta_chain.generate_prompt(
            style=style,
            highlighted_text=highlighted_text,
            shot_description=shot_description,
            directors_notes=directors_notes,
            script=script_excerpt,
            stick_to_script=stick_to_script,
            end_parameters=end_parameters,
            active_subjects=active_subjects,
            full_script=full_script,
            shot_configuration=camera_settings,
            length="detailed",
            director_style=director_style
        )

        # 3. Format prompts with style prefix/suffix if needed
        if style:
            style_data = self.style_manager.get_style(style)
            style_prefix = style_data.get("Prefix", "")
            style_suffix = style_data.get("Suffix", "")
            formatted_prompts = {}
            for prompt_type, prompt in prompts.items():
                formatted_prompt = f"{style_prefix}{prompt}{style_suffix}"
                formatted_prompts[prompt_type] = formatted_prompt
        else:
            formatted_prompts = prompts

        # 4. Prepare the return values
        concise_prompt = formatted_prompts.get("concise", "")
        normal_prompt = formatted_prompts.get("normal", "")
        detailed_prompt = formatted_prompts.get("detailed", "")
        structured_prompt = formatted_prompts.get("structured", "")
        generation_message = "Prompts generated successfully."
        active_subjects_display = ", ".join([subject["Name"] for subject in active_subjects])

        return (
            concise_prompt,
            normal_prompt,
            detailed_prompt,
            structured_prompt,
            generation_message,
            active_subjects_display
        )
from utils.style_manager import StyleManager
from components.subject_management import SubjectManager

class ScriptPromptGenerator:
    def __init__(self, style_manager: StyleManager, subject_manager: SubjectManager):
        self.style_manager = style_manager
        self.subject_manager = subject_manager

    def generate_prompt(self, script_excerpt: str, shot_description: str, directors_notes: str) -> str:
        # Placeholder implementation
        return f"Generated prompt based on:\nScript: {script_excerpt}\nShot: {shot_description}\nNotes: {directors_notes}"
