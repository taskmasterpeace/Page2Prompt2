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
        shot: Optional[str] = None,
        move: Optional[str] = None,
        size: Optional[str] = None,
        framing: Optional[str] = None,
        depth_of_field: Optional[str] = None,
        camera_type: Optional[str] = None,
        camera_name: Optional[str] = None,
        lens_type: Optional[str] = None,
        end_parameters: Optional[str] = None,
        stick_to_script: bool = False,
        highlighted_text: Optional[str] = None,
        full_script: Optional[str] = None,
        active_subjects: List[str] = []
    ) -> Tuple[str, str, str, str, str, str]:
        # Create camera_settings dictionary
        camera_settings = {
            "shot": shot or "",
            "move": move or "",
            "size": size or "",
            "framing": framing or "",
            "depth_of_field": depth_of_field or "",
            "camera_type": camera_type or "",
            "camera_name": camera_name or "",
            "lens_type": lens_type or ""
        }

        # 1. Get active subjects from SubjectManager
        active_subject_objects = [s for s in self.subject_manager.get_subjects() if s.name in active_subjects]

        # 2. Generate prompts using MetaChain (interacting with the LLM)
        prompts = await self.meta_chain.generate_prompt(
            style=style,
            highlighted_text=highlighted_text,
            shot_description=shot_description,
            directors_notes=directors_notes,
            script=script_excerpt if stick_to_script else None,
            stick_to_script=stick_to_script,
            end_parameters=end_parameters,
            active_subjects=[{"Name": s.name, "Description": s.description, "Alias": s.alias, "Type": s.type, "Prefix": s.prefix, "Suffix": s.suffix, "Active": s.active} for s in active_subject_objects],
            full_script=full_script if stick_to_script else None,
            shot_configuration=camera_settings,
            director_style=director_style
        )

        # 3. Apply aliases and prefix/suffix, then format the prompts
        formatted_prompts = {}
        for prompt_type, prompt in prompts.items():
            prompt = self.subject_manager.apply_alias(prompt)
            prompt = self.subject_manager.apply_prefix_suffix(prompt)
            formatted_prompt = f"{style_prefix.strip() + ' ' if style_prefix else ''}{prompt.strip()}{' ' + style_suffix.strip() if style_suffix else ''}"
            if end_parameters:
                formatted_prompt += f" {end_parameters.strip()}"
            formatted_prompts[prompt_type] = formatted_prompt

        # 4. Prepare the output tuple
        return (
            formatted_prompts.get("concise", ""),
            formatted_prompts.get("normal", ""),
            formatted_prompts.get("detailed", ""),
            formatted_prompts.get("structured", ""),
            "Prompts generated successfully",
            ", ".join([subject.name for subject in active_subject_objects])
        )
