import os
from dotenv import load_dotenv
from page2prompt.components.project_management import ProjectManager
from page2prompt.components.style_management import StyleManager
from page2prompt.api.subject_management import SubjectManager
from page2prompt.api.director_assistant import DirectorAssistant
from page2prompt.api.shot_list_generation import ShotListGenerator
from page2prompt.components.prompt_generation import PromptGenerator
from page2prompt.api.audio_processing import AudioProcessor

class Config:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.styles_file = os.getenv("STYLES_FILE", "styles.csv")
        self.subjects_file = os.getenv("SUBJECTS_FILE", "subjects.csv")
        self.director_styles_file = os.getenv("DIRECTOR_STYLES_FILE", "director_styles.csv")
        
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the page2prompt directory
        page2prompt_dir = os.path.dirname(current_dir)
        
        self.project_manager = ProjectManager()
        self.style_manager = StyleManager(os.path.join(page2prompt_dir, self.styles_file))
        self.subject_manager = SubjectManager(os.path.join(page2prompt_dir, self.subjects_file))
        self.director_assistant = DirectorAssistant(os.path.join(page2prompt_dir, self.director_styles_file))
        self.shot_list_generator = ShotListGenerator(self.openai_api_key, self.subject_manager, self.style_manager, self.director_assistant)
        self.prompt_generator = PromptGenerator()
        self.audio_processor = AudioProcessor()

    def get_openai_api_key(self):
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        return self.openai_api_key

config = Config()
