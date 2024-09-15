import asyncio
from typing import Dict, List, Optional
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from utils.style_manager import StyleManager
from ..utils.subject_manager import SubjectManager
from ..components.meta_chain import MetaChain

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
        style_prefix: Optional[str] = None,
        style_suffix: Optional[str] = None,
        director_style: Optional[str] = None,
        camera_settings: Optional[Dict[str, str]] = None,
        end_parameters: Optional[str] = None,
        stick_to_script: bool = False,
        highlighted_text: Optional[str] = None,
        full_script: Optional[str] = None,
    ) -> Dict[str, str]:
        # 1. Get active subjects from SubjectManager
        active_subjects = self.subject_manager.get_active_subjects()

        # 2. Generate prompts using MetaChain (interacting with the LLM)
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

        # 3. Format the generated prompts using the style prefix/suffix
        formatted_prompts = {}
        for prompt_type, prompt in prompts.items():
            formatted_prompt = f"{style_prefix or ''}{prompt}{style_suffix or ''}"
            formatted_prompts[prompt_type] = formatted_prompt

        return formatted_prompts
from utils.style_manager import StyleManager
from components.subject_management import SubjectManager

class ScriptPromptGenerator:
    def __init__(self, style_manager: StyleManager, subject_manager: SubjectManager):
        self.style_manager = style_manager
        self.subject_manager = subject_manager

    def generate_prompt(self, script_excerpt: str, shot_description: str, directors_notes: str) -> str:
        # Placeholder implementation
        return f"Generated prompt based on:\nScript: {script_excerpt}\nShot: {shot_description}\nNotes: {directors_notes}"
