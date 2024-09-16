import os
from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import get_openai_callback
import langsmith

# Initialize LangSmith
langsmith.set_project("page2prompt")

class MetaChain:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-0613")

    def _get_prompt_template(self) -> ChatPromptTemplate:
        template = """
        Generate creative prompts for a script based on the following information:

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
        - Camera Shot: {shot_configuration.shot}
        - Camera Movement: {shot_configuration.move}
        - Shot Size: {shot_configuration.size}
        - Framing: {shot_configuration.framing}
        - Depth of Field: {shot_configuration.depth_of_field}
        Length: {length}
        Director's Style: {director_style}

        Please generate three prompts:
        1. A concise prompt (about 20 words)
        2. A normal prompt (about 50 words)
        3. A detailed prompt (about 100 words)

        Ensure that the prompts incorporate the provided information and are creative and coherent.
        """
        return ChatPromptTemplate.from_template(template)

    async def generate_prompt(self, **kwargs: Any) -> Dict[str, str]:
        prompt_template = self._get_prompt_template()
        
        # Prepare the input for the prompt template
        input_dict = {
            "style": kwargs.get("style", ""),
            "highlighted_text": kwargs.get("highlighted_text", ""),
            "shot_description": kwargs.get("shot_description", ""),
            "directors_notes": kwargs.get("directors_notes", ""),
            "script": kwargs.get("script", ""),
            "stick_to_script": str(kwargs.get("stick_to_script", False)),
            "end_parameters": kwargs.get("end_parameters", ""),
            "active_subjects": ", ".join([s["Name"] for s in kwargs.get("active_subjects", [])]),
            "full_script": kwargs.get("full_script", ""),
            "shot_configuration": kwargs.get("shot_configuration", {}),
            "length": kwargs.get("length", "normal"),
            "director_style": kwargs.get("director_style", "")
        }

        try:
            with get_openai_callback() as cb:
                result = await self.llm.agenerate([prompt_template.format_messages(**input_dict)])
                
            # Parse the result to extract the three prompts
            content = result.generations[0][0].text
            prompts = content.split("\n\n")
            
            return {
                "concise": prompts[0].strip() if len(prompts) > 0 else "",
                "normal": prompts[1].strip() if len(prompts) > 1 else "",
                "detailed": prompts[2].strip() if len(prompts) > 2 else "",
                "structured": content  # Keep the full structured output
            }
        except Exception as e:
            print(f"Error generating prompt: {str(e)}")
            return {
                "concise": "Error generating concise prompt",
                "normal": "Error generating normal prompt",
                "detailed": "Error generating detailed prompt",
                "structured": f"Error: {str(e)}"
            }
