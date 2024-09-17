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
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini", openai_api_key=self.api_key)

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
        Camera Shot: {camera_shot}
        Camera Move: {camera_move}
        Camera Size: {camera_size}
        Framing: {camera_framing}
        Depth of Field: {camera_depth_of_field}
        Camera Type: {camera_type}
        Camera Name: {camera_name}
        Lens Type: {camera_lens_type}

        Important:
        1. Integrate Camera Work Seamlessly: Incorporate the camera work description seamlessly into the scene description.
        2. Positive Descriptions: Describe the scene positively. Avoid phrases like "no additional props" or "no objects present." Focus on what is in the scene.
        3. Include Provided Camera Information Only: Only include camera information if it's provided in the input.
        4. Exclude Style Information from Prompts: Never include style information or stylistic adjectives (like 'vibrant', 'moody') in the image prompt unless specified in the Director's Notes, Director's Style, or character description. Style is handled in the Style and Style Prefix only.
        5. Generate Three Separate Paragraphs: Generate three separate paragraphs without headings:
           Concise: About 20 words. Do not include the camera name in this prompt.
           Normal: About 50 words.
           Detailed: About 100 words.
           Separate each paragraph with a space.
        6. Consider Depth and Placement: Think about the main subject's placement to create depth. Include elements in the foreground, middle ground, and background to enhance dimension. Use specified foreground elements to frame the subject or add depth. Balance these elements for a cohesive and visually interesting composition.
        7. Adapt Subject Descriptions Based on Framing:
           Close-ups:
           - People: Focus on facial features, expressions, and upper body details visible in the frame.
           - Animals: Highlight distinguishing features, textures, and expressions that are prominent in a close-up.
           - Objects/Things: Emphasize key details, textures, and defining characteristics of the item.
           - Places: Zoom in on specific elements or features of the location that are important or visually striking.
           Medium Shots:
           - People: Describe visible clothing, posture, and general body language.
           - Animals: Include the animal's posture, movement, and notable physical traits.
           - Objects/Things: Provide an overview of the object's size, shape, and how it interacts with its immediate surroundings.
           - Places: Capture a portion of the location, showing context and how elements within the space relate to each other.
           Wide or Establishing Shots:
           - People and Animals: Mention their placement within the larger scene, focusing on actions or interactions visible from a distance.
           - Objects/Things: Describe the object's position in relation to the environment, emphasizing its role or significance within the setting.
           - Places: Provide a broad view of the location, highlighting major landmarks, landscapes, or spatial relationships that define the setting.
        8. Ensure Consistency Across Prompts: Prioritize the most important visual elements for each shot type to maintain consistency across the three prompt lengths.
        9. Balance Elements in Each Prompt: For each prompt length, maintain a balance between character details, setting description, and action appropriate to the shot type and framing.
        10. Include Relevant Subject Details: Incorporate descriptions of active subjects provided in the 'Subjects' field into the prompts, but only include details visible in the current shot type.
        11. Script Adherence: {script_adherence}
        12. Avoid Unnecessary Phrases: Do not include meta-commentary or evaluative statements about the composition, such as "The overall composition captures...". Focus on directly describing the scene.
        13. Position of Camera Name: Place the camera name at the end of the normal and detailed prompts. It is not a priority item like shot size and should not be included in the concise prompt unless essential.

        Prompt Structure:
        Implement a modular structure that prioritizes key elements in this order:
        [Camera Movement only if provided; if provided, must start prompt with it] [Shot Size] of [Subject(s)][Subject Description relevant to shot size] [Action/Pose] in [Setting: interior or exterior].

        [Camera Settings: Name, Lens Type, etc.]

        [Additional Details: Foreground elements to reinforce the setting, background elements to further set the setting, time of day to dictate the lighting, depth of field effects, etc.]

        Guidelines:
        - Start with the subject: Begin your prompt by clearly stating the main subject or focus of the image.
        - Use descriptive language: Provide detailed descriptions of the subject and environment.
        - Include technical details: Incorporate camera angles, lighting conditions, or other technical aspects to further guide the image generation.
        - Add modifiers: Include adjectives and descriptive phrases to refine the image's appearance, mood, and style. Do not add style elements that is handled in the Style and Style Prefix only. The key is to provide clear, descriptive information about what you want to see in the image.

        Prompts:
        """
        return PromptTemplate(
            input_variables=[
                "style", "style_prefix", "shot_description", "directors_notes",
                "highlighted_text", "full_script", "subject_info", "end_parameters",
                "script_adherence", "director_style", "camera_shot", "camera_move",
                "camera_size", "camera_framing", "camera_depth_of_field", "camera_type",
                "camera_name", "camera_lens_type"
            ],
            template=base_template
        )

    async def generate_prompt(self, style: Optional[str], highlighted_text: Optional[str], shot_description: str, directors_notes: str, script: Optional[str], stick_to_script: bool, end_parameters: str, active_subjects: Optional[List[Dict[str, Any]]] = None, full_script: str = "", shot_configuration: Optional[Dict[str, str]] = None, director_style: Optional[str] = None, style_prefix: Optional[str] = None) -> Dict[str, str]:
        prompt_template = self._get_prompt_template()
        
        shot_config = shot_configuration or {}
        camera_settings = {
            "camera_shot": shot_config.get("shot", ""),
            "camera_move": shot_config.get("move", ""),
            "camera_size": shot_config.get("size", ""),
            "camera_framing": shot_config.get("framing", ""),
            "camera_depth_of_field": shot_config.get("depth_of_field", ""),
            "camera_type": shot_config.get("camera_type", ""),
            "camera_name": shot_config.get("camera_name", ""),
            "camera_lens_type": shot_config.get("lens_type", "")
        }
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
            **camera_settings
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
            error_message = f"Error generating prompt: {str(e)}"
            print(error_message)
            return {
                "concise": error_message,
                "normal": error_message,
                "detailed": error_message,
                "structured": error_message
            }
