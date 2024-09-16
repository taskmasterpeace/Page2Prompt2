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

    def _get_prompt_template(self, length: str) -> PromptTemplate:
        template = """
        Generate a {length} creative prompt for a script based on the following information:

        Style: {style}
        Highlighted Text: {highlighted_text}
        Shot Description: {shot_description}
        Director's Notes: {directors_notes}
        Script Excerpt: {script}
        Stick to Script: {stick_to_script}
        End Parameters: {end_parameters}
        Active Subjects: {active_subjects}
        Full Script: {full_script}
        Shot Configuration:
        - Camera Shot: {shot_configuration[shot]}
        - Camera Movement: {shot_configuration[move]}
        - Shot Size: {shot_configuration[size]}
        - Framing: {shot_configuration[framing]}
        - Depth of Field: {shot_configuration[depth_of_field]}
        Director's Style: {director_style}

        Ensure that the prompt incorporates the provided information and is creative and coherent.
        """
        return PromptTemplate.from_template(template)

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", shot_configuration: Optional[Dict[str, str]] = None, length: str = "detailed", director_style: Optional[str] = None) -> Dict[str, str]:
        prompt_template = self._get_prompt_template(length)
        
        input_dict = {
            "style": style or "",
            "highlighted_text": highlighted_text or "",
            "shot_description": shot_description,
            "directors_notes": directors_notes,
            "script": script or "",
            "stick_to_script": str(stick_to_script),
            "end_parameters": end_parameters,
            "active_subjects": ", ".join([s["Name"] for s in (active_subjects or [])]),
            "full_script": full_script,
            "shot_configuration": shot_configuration or {},
            "length": length,
            "director_style": director_style or ""
        }

        try:
            with get_openai_callback() as cb:
                chain = RunnableSequence(
                    prompt_template,
                    self.llm
                )
                result = await chain.ainvoke(input_dict)
                
            content = result.content
            
            return {
                "concise": content if length == "concise" else "",
                "normal": content if length == "normal" else "",
                "detailed": content if length == "detailed" else "",
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
