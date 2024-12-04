import gradio as gr
from page2prompt.api.prompt_generation import PromptGenerator
from page2prompt.components.project_management import ProjectManager
from page2prompt.api.subject_management import SubjectManager
from page2prompt.components.style_management import StyleManager
from page2prompt.components.meta_chain import MetaChain
from page2prompt.models.shot import Shot

from page2prompt.api.prompt_generation import PromptGenerator

from page2prompt.api.prompt_generation import PromptGenerator

async def generate_prompts_handler(
    shot_description,
    directors_notes,
    full_script,
    style,
    style_prefix,
    style_suffix,
    director_style,
    people,
    places,
    props,
    shot,
    move,
    size,
    framing,
    depth_of_field,
    camera_type,
    camera_name,
    lens_type,
    end_parameters,
    style_manager,
    subject_manager
):
    try:
        prompt_generator = PromptGenerator(style_manager, subject_manager)
        prompt = await prompt_generator.generate_prompts(
            shot_description=shot_description,
            directors_notes=directors_notes,
            full_script=full_script,
            style=style,
            style_prefix=style_prefix,
            style_suffix=style_suffix,
            director_style=director_style,
            people=people,
            places=places,
            props=props,
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
        return prompt.concise, prompt.normal, prompt.detailed, prompt.structured, "Prompts generated successfully", prompt.active_subjects
    except Exception as e:
        return "", "", "", "", f"Error generating prompts: {str(e)}", ""

from page2prompt.api.shot_list_generation import ShotListGenerator

async def generate_bulk_notes_handler(api_key, subject_manager, style_manager, director_assistant, *args):
    shot_list_generator = ShotListGenerator(api_key, subject_manager, style_manager, director_assistant)
    return await shot_list_generator.generate_bulk_directors_notes(*args)

async def generate_bulk_prompts_handler(api_key, subject_manager, style_manager, director_assistant, *args):
    shot_list_generator = ShotListGenerator(api_key, subject_manager, style_manager, director_assistant)
    return await shot_list_generator.generate_bulk_prompts(*args)

async def save_project_handler(project_manager: ProjectManager, *args):
    return await project_manager.save_project(*args)

async def load_project_handler(project_manager: ProjectManager, *args):
    return await project_manager.load_project(*args)

async def delete_project_handler(project_manager: ProjectManager, *args):
    return await project_manager.delete_project(*args)

def add_subject_handler(subject_manager: SubjectManager, *args):
    return subject_manager.add_subject(*args)

def update_subject_handler(subject_manager: SubjectManager, *args):
    return subject_manager.update_subject(*args)

def delete_subject_handler(subject_manager: SubjectManager, *args):
    return subject_manager.delete_subject(*args)

def import_subjects_handler(subject_manager: SubjectManager, file):
    if file is not None:
        try:
            subject_manager.import_subjects(file.name)
            return subject_manager.get_subjects_dataframe(), "Subjects imported successfully."
        except Exception as e:
            return subject_manager.get_subjects_dataframe(), f"Error importing subjects: {str(e)}"
    return subject_manager.get_subjects_dataframe(), "No file selected for import."

def export_subjects_handler(subject_manager: SubjectManager):
    subject_manager.export_subjects()
    return "Subjects exported successfully."

def receive_proposed_subjects_handler(subject_manager: SubjectManager, script_manager):
    proposed_subjects_df = script_manager.get_proposed_subjects()
    if proposed_subjects_df.empty:
        return None, "No proposed subjects available."
    
    existing_df = subject_manager.get_subjects_dataframe()
    updated_df = subject_manager.merge_subjects(existing_df, proposed_subjects_df)
    subject_manager.set_subjects(updated_df)
    return updated_df, "Subjects received and merged successfully."

def generate_random_style_handler(style_manager: StyleManager):
    message, new_style = style_manager.generate_random_style()
    return message, gr.Dropdown(choices=style_manager.get_styles(), value=new_style)

def transcribe_audio_handler(audio_processor, audio_file, include_timestamps):
    if audio_file is None:
        return "Please upload an MP3 file."
    return audio_processor.transcribe_audio(audio_file, include_timestamps)

def search_and_replace_lyrics_handler(audio_processor, lyrics, find, replace):
    return audio_processor.search_and_replace_lyrics(lyrics, find, replace)
