import gradio as gr
from page2prompt.ui.app_builder import create_gradio_app
from page2prompt.components.style_management import StyleManager
from page2prompt.api.subject_management import SubjectManager
from page2prompt.api.prompt_generation import PromptGenerator
from page2prompt.api.director_assistant import DirectorAssistant
from page2prompt.components.project_management import ProjectManager
from page2prompt.api.shot_list_generation import ShotListGenerator
from page2prompt.api.audio_processing import AudioProcessor

import os
from page2prompt.components.script_management import ScriptManager

class Config:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.style_manager = StyleManager(os.path.join("page2prompt", "styles.csv"))
        self.subject_manager = SubjectManager(os.path.join("page2prompt", "subjects.csv"))
        self.director_assistant = DirectorAssistant(os.path.join("page2prompt", "director_styles.csv"))
        self.project_manager = ProjectManager()
        self.prompt_generator = PromptGenerator(self.style_manager, self.subject_manager)
        self.audio_processor = AudioProcessor()
        self.script_manager = ScriptManager()

# Initialize configuration
config = Config()

# Launch the Gradio app
if __name__ == "__main__":
    demo = create_gradio_app(config)
    demo.launch()

