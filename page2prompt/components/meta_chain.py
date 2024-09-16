import os
from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

class MetaChain:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0613", openai_api_key=self.api_key)

    def _get_prompt_template(self) -> PromptTemplate:
        base_template = """
        Generate three prompts (concise, normal, and detailed) based on the following information:

        Subjects: {subject_info}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Highlighted Script: {highlighted_text}
        Full Script: {full_script}
        End Parameters: {end_parameters}
        Style: {style}
        Style Prefix: {style_prefix}
        Director's Style: {director_style}
        Camera Shot: {shot_configuration[shot]}
        Camera Move: {shot_configuration[move]}
        Camera Size: {shot_configuration[size]}
        Framing: {shot_configuration[framing]}
        Depth of Field: {shot_configuration[depth_of_field]}

        Important:
        1. Incorporate the camera work description seamlessly into the scene description.
        2. Describe the scene positively. Don't use phrases like "no additional props" or "no objects present". Instead, focus on what is in the scene.
        3. Only include camera information if it's provided in the input.
        4. Never include style information in the image prompt. That is done in the Style and Style Prefix Only.
        5. Generate three separate paragraphs: concise (about 20 words), normal (about 50 words), and detailed (about 100 words). Separate them by a space. Do not add headings for these.
        6. Consider the main subject and its placement. Think about depth. Include elements in the foreground, middle ground, and background to create a sense of dimension when the shot requires it; do not force it.
        7. Adapt character descriptions based on the framing of the shot:
           - For close-ups, focus on facial features, expressions, and upper body details visible in the frame.
           - For medium shots, describe visible clothing, posture, and general body language.
           - For wide or establishing shots, mention only broad, distinguishing characteristics visible from a distance.
        8. Ensure consistency across the three prompt lengths, prioritizing the most important visual elements for each shot type.
        9. For each prompt length, maintain a balance between character details, setting description, and action, appropriate to the shot type and framing.
        10. Incorporate the descriptions of active subjects provided in the 'Subjects' field into the prompts, but only include details that would be visible in the current shot type.
        11. {script_adherence}

        Prompts:
        """
        return PromptTemplate(
            input_variables=[
                "style", "style_prefix", "shot_description", "directors_notes",
                "highlighted_text", "full_script", "subject_info", "end_parameters",
                "script_adherence", "director_style", "shot_configuration"
            ],
            template=base_template
        )

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", shot_configuration: Optional[Dict[str, str]] = None, director_style: Optional[str] = None, style_prefix: Optional[str] = None) -> Dict[str, str]:
        prompt_template = self._get_prompt_template()
        
        shot_config = shot_configuration or {}
        subject_info = ", ".join([f"{s['Name']}: {s['Description']}" for s in (active_subjects or [])])
        script_adherence = "Strictly adhere to the script content." if stick_to_script else "You can be creative with the script content while maintaining its essence."

        input_dict = {
            "style": style or "",
            "style_prefix": style_prefix or "",
            "highlighted_text": highlighted_text or "",
            "shot_description": shot_description,
            "directors_notes": directors_notes,
            "full_script": full_script,
            "subject_info": subject_info,
            "end_parameters": end_parameters,
            "script_adherence": script_adherence,
            "director_style": director_style or "",
            "shot_configuration": shot_config
        }

        try:
            with get_openai_callback() as cb:
                chain = RunnableSequence(
                    prompt_template,
                    self.llm
                )
                result = await chain.ainvoke(input_dict)
                
            content = result.content
            prompts = content.split('\n\n')
            
            return {
                "concise": prompts[0] if len(prompts) > 0 else "",
                "normal": prompts[1] if len(prompts) > 1 else "",
                "detailed": prompts[2] if len(prompts) > 2 else "",
                "structured": content
            }
        except Exception as e:
            print(f"Error generating prompt: {str(e)}")
            return {
                "concise": "Error generating concise prompt",
                "normal": "Error generating normal prompt",
                "detailed": "Error generating detailed prompt",
                "structured": f"Error: {str(e)}"
            }
