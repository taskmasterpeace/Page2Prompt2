import asyncio
from typing import Dict, List, Optional, Tuple
from ..utils.style_manager import StyleManager
from ..utils.subject_manager import SubjectManager
from .meta_chain import MetaChain

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

        # 3. Format the generated prompts using the style prefix/suffix and append end_parameters
        formatted_prompts = {}
        for prompt_type, prompt in prompts.items():
            formatted_prompt = f"{style_prefix + ' ' if style_prefix else ''}{prompt}{' ' + style_suffix if style_suffix else ''}"
            if end_parameters:
                formatted_prompt += f" {end_parameters}"
            formatted_prompts[prompt_type] = formatted_prompt

        # 4. Prepare the output dictionary
        output = {
            "concise_prompt": formatted_prompts.get("concise", ""),
            "normal_prompt": formatted_prompts.get("normal", ""),
            "detailed_prompt": formatted_prompts.get("detailed", ""),
            "structured_prompt": formatted_prompts.get("structured", ""),
            "generation_message": "Prompts generated successfully",
            "active_subjects_display": ", ".join([subject["Name"] for subject in active_subjects])
        }

        return output
import asyncio
from typing import Dict, List, Optional, Tuple
from page2prompt.utils.style_manager import StyleManager
from page2prompt.utils.subject_manager import SubjectManager
from page2prompt.components.meta_chain import MetaChain

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

        # 3. Format the generated prompts using the style prefix/suffix and append end_parameters
        formatted_prompts = {}
        for prompt_type, prompt in prompts.items():
            formatted_prompt = f"{style_prefix or ''}{prompt}{style_suffix or ''}"
            if end_parameters:
                formatted_prompt += f" {end_parameters}"
            formatted_prompts[prompt_type] = formatted_prompt

        # 4. Prepare the output tuple
        return (
            formatted_prompts.get("concise", ""),
            formatted_prompts.get("normal", ""),
            formatted_prompts.get("detailed", ""),
            formatted_prompts.get("structured", ""),
            "Prompts generated successfully",
            ", ".join([subject["Name"] for subject in active_subjects])
        )
