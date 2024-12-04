import os
import logging
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.callbacks.manager import get_openai_callback
from page2prompt.components.style_management import StyleManager
from page2prompt.api.subject_management import SubjectManager
from page2prompt.models.prompt import Prompt

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PromptGenerator:
    def __init__(self, style_manager: StyleManager, subject_manager: SubjectManager):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found in environment variables")
        logger.info("API key found and set")
        
        try:
            self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0125-preview", openai_api_key=self.api_key)
            self.style_manager = style_manager
            self.subject_manager = subject_manager
            logger.info("PromptGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing PromptGenerator: {str(e)}")
            raise

    def _get_prompt_template(self) -> PromptTemplate:
        base_template = """
        Generate three prompts (concise, normal, and detailed) based on the following information:

        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Full Script: {full_script}
        Style: {style}
        Director's Style: {director_style}
        People: {people}
        Places: {places}
        Props: {props}
        Shot: {shot}
        Move: {move}
        Size: {size}
        Framing: {framing}
        Depth of Field: {depth_of_field}
        Camera Type: {camera_type}
        Camera Name: {camera_name}
        Lens Type: {lens_type}
        End Parameters: {end_parameters}

        Guidelines:
        1. Concise: About 20 words.
        2. Normal: About 50 words.
        3. Detailed: About 100 words.
        4. Focus on describing the scene visually.
        5. Incorporate style elements subtly.
        6. Include camera work if specified.

        Prompts:
        """
        return PromptTemplate(
            input_variables=["shot_description", "directors_notes", "full_script", "style", "director_style",
                             "people", "places", "props", "shot", "move", "size", "framing", "depth_of_field",
                             "camera_type", "camera_name", "lens_type", "end_parameters"],
            template=base_template
        )

    async def generate_prompts(self, shot_description: str, directors_notes: str, full_script: str, style: str,
                               style_prefix: str, style_suffix: str, director_style: str, people: List[str],
                               places: List[str], props: List[str], shot: str, move: str, size: str,
                               framing: str, depth_of_field: str, camera_type: str, camera_name: str,
                               lens_type: str, end_parameters: str) -> Prompt:
        try:
            logger.info("Generating prompts")
            style_info = self.style_manager.get_style_details(style)
            style_prefix = style_prefix or (style_info['prefix'] if style_info else "")
            style_suffix = style_suffix or (style_info['suffix'] if style_info else "")

            prompts = await self._generate_prompt(
                shot_description=shot_description,
                directors_notes=directors_notes,
                full_script=full_script,
                style=style,
                director_style=director_style,
                people=", ".join(people),
                places=", ".join(places),
                props=", ".join(props),
                shot=shot,
                move=move,
                size=size,
                framing=framing,
                depth_of_field=depth_of_field,
                camera_type=camera_type,
                camera_name=camera_name,
                lens_type=lens_type,
                end_parameters=end_parameters
            )
            
            formatted_prompts = {
                k: f"{style_prefix} {v} {style_suffix}".strip()
                for k, v in prompts.items()
            }

            return Prompt(
                concise=formatted_prompts.get("concise", ""),
                normal=formatted_prompts.get("normal", ""),
                detailed=formatted_prompts.get("detailed", "")
            )
        except Exception as e:
            logger.error(f"Error generating prompts: {str(e)}", exc_info=True)
            return Prompt("", "", "")

    async def _generate_prompt(self, **kwargs) -> Dict[str, str]:
        prompt_template = self._get_prompt_template()

        try:
            with get_openai_callback() as cb:
                chain = RunnableSequence(
                    prompt_template,
                    self.llm
                )
                result = await chain.ainvoke(kwargs)
                
            content = result.content
            prompts = content.split('\n\n')
            
            return {
                "concise": prompts[0] if len(prompts) > 0 else "",
                "normal": prompts[1] if len(prompts) > 1 else "",
                "detailed": prompts[2] if len(prompts) > 2 else ""
            }
        except Exception as e:
            error_message = f"Error generating prompt: {str(e)}"
            logger.error(error_message)
            return {
                "concise": error_message,
                "normal": error_message,
                "detailed": error_message
            }
