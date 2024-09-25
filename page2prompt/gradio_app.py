import gradio as gr
import asyncio
import csv
import os
import pandas as pd
import json
from datetime import datetime
import logging

def import_prompts_from_file(file):
    if file is not None:
        content = file.decode('utf-8')
        return content
    return ""

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize generated_prompts
generated_prompts = []
from .components.script_prompt_generation import ScriptPromptGenerator
from .utils.subject_manager import SubjectManager, Subject
from .utils.style_manager import StyleManager
from .components.meta_chain import MetaChain
from .utils.shot_list_generator import generate_shot_list
from .components.director_assistant import DirectorAssistant
from .music_lab import transcribe_audio, search_and_replace_lyrics
from .utils.script_manager import ScriptManager

# Add debug print statements
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir())

# Define data directory
DATA_DIR = os.path.dirname(__file__)

# Initialize components with error handling
try:
    style_manager = StyleManager(os.path.join(DATA_DIR, "styles.csv"))
    print(f"Available styles: {style_manager.get_styles()}")
except Exception as e:
    print(f"Error loading styles: {str(e)}")

try:
    subject_manager = SubjectManager(os.path.join(DATA_DIR, "subjects.csv"))
except Exception as e:
    print(f"Error loading subjects: {str(e)}")
meta_chain = MetaChain()
script_prompt_generator = ScriptPromptGenerator(style_manager, subject_manager, meta_chain)
director_assistant = DirectorAssistant(os.path.join(DATA_DIR, "director_styles.csv"))
script_manager = ScriptManager(meta_chain)

async def handle_conversation(user_input, concept, genre, descriptors, lyrics, chat_history):
    # Placeholder function for handling conversation
    # You should implement the actual conversation logic here
    updated_history = chat_history + [("User", user_input), ("Assistant", "This is a placeholder response.")]
    return updated_history, updated_history

# Load camera settings from CSV
def load_camera_settings(csv_file):
    settings = {}
    file_path = os.path.join(DATA_DIR, csv_file)
    print(f"Attempting to load camera settings from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['type'] not in settings:
                    settings[row['type']] = []
                settings[row['type']].append(row['display'])
        print(f"Successfully loaded camera settings")
    except Exception as e:
        print(f"Error loading camera settings: {str(e)}")
    return settings

camera_settings = load_camera_settings("camera_settings.csv")

# Load director styles from CSV
def load_director_styles(csv_file):
    styles = []
    file_path = os.path.join(DATA_DIR, csv_file)
    print(f"Attempting to load director styles from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            styles = list(reader)
        print(f"Successfully loaded director styles")
    except Exception as e:
        print(f"Error loading director styles: {str(e)}")
    return styles

director_styles = load_director_styles("director_styles.csv")

# Transcribe audio function
def transcribe_audio_wrapper(audio_file, include_timestamps):
    if audio_file is None:
        return "Please upload an MP3 file."
    return transcribe_audio(audio_file, include_timestamps)

# Gradio interface setup
with gr.Blocks() as demo:
    with gr.Accordion("🎬 Script & Director Style", open=True):
        director_style_input = gr.Dropdown(label="🎬 Director Style", choices=["No Director"] + [style['name'] for style in director_styles])
        with gr.Accordion("📜 Full Script", open=False):
            with gr.Row():
                full_script_input = gr.Textbox(label="📚 Full Script", lines=10)
                copy_full_script_btn = gr.Button("📋 Send to Clipboard", scale=1)

    with gr.Tabs():
        with gr.TabItem("🎥 Shot and Prompt Generation"):
            with gr.Row():
                with gr.Column():
                    with gr.Accordion("📝 Shot Details", open=True):
                        shot_description_input = gr.Textbox(label="📸 Shot Description")
                        directors_notes_input = gr.Textbox(label="🎬 Director's Notes")
                        stick_to_script_input = gr.Checkbox(label="📜 Stick to Script")
                        highlighted_text_input = gr.Textbox(label="🖍️ Highlighted Text")

                    with gr.Accordion("👥 Subjects", open=False):
                        with gr.Row():
                            with gr.Column():
                                people = gr.CheckboxGroup(label="People", choices=subject_manager.get_people())
                            with gr.Column():
                                places = gr.CheckboxGroup(label="Places", choices=subject_manager.get_places())
                            with gr.Column():
                                props = gr.CheckboxGroup(label="Props", choices=subject_manager.get_props())

                    with gr.Accordion("🎨 Style", open=False):
                        with gr.Row():
                            style_input = gr.Dropdown(label="Style", choices=style_manager.get_styles())
                            style_prefix_input = gr.Textbox(label="Prefix")
                            style_suffix_input = gr.Textbox(label="Suffix")
                        
                        with gr.Row():
                            save_style_btn = gr.Button("💾 Save Style")
                            delete_style_btn = gr.Button("🗑️ Delete Style")
                            random_style_btn = gr.Button("🎲 Generate Random Style")
                            generate_style_details_btn = gr.Button("✨ Generate Style Details")

                        end_parameters_input = gr.Textbox(label="🔚 End Parameters")

                        def update_style_fields(style_name):
                            style = style_manager.get_style(style_name)
                            return style.get("Prefix", ""), style.get("Suffix", "")

                        style_input.change(
                            update_style_fields,
                            inputs=[style_input],
                            outputs=[style_prefix_input, style_suffix_input]
                        )

                    with gr.Accordion("📷 Camera Settings", open=False):
                        with gr.Row():
                            shot = gr.Dropdown(label="Shot", choices=["AI Suggest"] + camera_settings.get('shot', []))
                            move = gr.Dropdown(label="Move", choices=["AI Suggest"] + camera_settings.get('move', []))
                            size = gr.Dropdown(label="Size", choices=["AI Suggest"] + camera_settings.get('size', []))
                        with gr.Row():
                            framing = gr.Dropdown(label="Framing", choices=["AI Suggest"] + camera_settings.get('framing', []))
                            depth_of_field = gr.Dropdown(label="Depth of Field", choices=["AI Suggest"] + camera_settings.get('depth_of_field', []))
                            camera_type = gr.Dropdown(label="Camera Type", choices=["AI Suggest"] + camera_settings.get('camera_type', []))
                        with gr.Row():
                            camera_name = gr.Dropdown(label="Camera Name", choices=["AI Suggest"] + camera_settings.get('camera_name', []))
                            lens_type = gr.Dropdown(label="Lens Type", choices=["AI Suggest"] + camera_settings.get('lens_type', []))

                    generate_button = gr.Button("🚀 Generate Prompts")

                with gr.Column():
                    with gr.Accordion("🖼️ Generated Prompts", open=True):
                        with gr.Row():
                            concise_prompt = gr.Textbox(label="Concise")
                            copy_concise_btn = gr.Button("📋 Send to Clipboard", scale=1)
                        with gr.Row():
                            normal_prompt = gr.Textbox(label="Normal")
                            copy_normal_btn = gr.Button("📋 Send to Clipboard", scale=1)
                        with gr.Row():
                            detailed_prompt = gr.Textbox(label="Detailed")
                            copy_detailed_btn = gr.Button("📋 Send to Clipboard", scale=1)
                        
                        send_all_prompts_btn = gr.Button("📤 Send All Prompts to Clipboard")
                        
                        structured_prompt = gr.Textbox(label="Structured Prompt")
                        generation_message = gr.Textbox(label="Generation Message")
                        active_subjects_display = gr.Textbox(label="Active Subjects")
                        
                        send_prompts_btn = gr.Button("📤 Send Prompts")

        with gr.TabItem("👥 Subject Management"):
            with gr.Row():
                subject_name = gr.Textbox(label="Name")
                subject_description = gr.Textbox(label="Description")
                subject_alias = gr.Textbox(label="Alias")
                subject_type = gr.Dropdown(label="Type", choices=["person", "place", "prop"])
                subject_prefix = gr.Textbox(label="Prefix")
                subject_suffix = gr.Textbox(label="Suffix")

            subjects_df = gr.DataFrame(
                headers=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"],
                datatype=["str", "str", "str", "str", "str", "str", "bool"],
                col_count=(7, "fixed"),
                interactive=True
            )

            with gr.Row():
                add_subject_btn = gr.Button("Add Subject")
                update_subject_btn = gr.Button("Update Subject")
                delete_subject_btn = gr.Button("Delete Subject")
                delete_row_btn = gr.Button("Delete Selected Row")
                import_subjects_btn = gr.Button("Import Subjects")
                export_subjects_btn = gr.Button("Export Subjects")
                receive_proposed_subjects_btn = gr.Button("Receive Proposed Subjects")

        with gr.TabItem("📋 Bulk Prompt Management"):
            with gr.Accordion("Director's Clipboard 🎬"):
                directors_clipboard = gr.TextArea(label="Collected Prompts 📝", lines=10, interactive=True)
                with gr.Row():
                    clear_clipboard_btn = gr.Button("🗑️ Clear Clipboard")
                    export_clipboard_btn = gr.Button("💾 Export Clipboard")
                    import_prompts_btn = gr.Button("📥 Import Prompts from File")

        with gr.TabItem("🗂️ Project Management"):
            with gr.Row():
                project_name_input = gr.Textbox(label="Project Name")
                save_project_btn = gr.Button("💾 Save Project")
                load_project_btn = gr.Button("📂 Load Project")
                delete_project_btn = gr.Button("🗑️ Delete Project")
                export_prompts_btn = gr.Button("📤 Export Prompts")

            projects_df = gr.DataFrame(
                headers=["Project Name", "Last Modified"],
                label="Saved Projects",
                interactive=False
            )

            prompts_display = gr.TextArea(label="Generated Prompts", lines=10, interactive=False)

            def update_prompts_display(prompts):
                return "\n\n".join(prompts)

            # Update the prompts display when loading a project
            load_project_btn.click(
                lambda prompts: update_prompts_display(prompts),
                inputs=[gr.State(lambda: generated_prompts)],
                outputs=[prompts_display]
            )
        
            project_info = gr.JSON(label="Project Info", visible=False)

            def add_subject(name, description, alias, type, prefix, suffix):
                new_subject = Subject(name, description, alias, type, prefix, suffix)
                subject_manager.add_subject(new_subject)
                return subject_manager.get_subjects_dataframe()

            def update_subject(name, description, alias, type, prefix, suffix):
                updated_subject = Subject(name, description, alias, type, prefix, suffix)
                subject_manager.update_subject(updated_subject)
                return subject_manager.get_subjects_dataframe()

            def delete_subject(name):
                subject_manager.delete_subject(name)
                return subject_manager.get_subjects_dataframe()

            def import_subjects(file):
                if file is not None:
                    subject_manager.import_subjects(file.name)
                return subject_manager.get_subjects_dataframe()

            def export_subjects():
                subject_manager.export_subjects("exported_subjects.csv")
                return "Subjects exported to exported_subjects.csv"

            add_subject_btn.click(
                add_subject,
                inputs=[subject_name, subject_description, subject_alias, subject_type, subject_prefix, subject_suffix],
                outputs=[subjects_df]
            )

            update_subject_btn.click(
                update_subject,
                inputs=[subject_name, subject_description, subject_alias, subject_type, subject_prefix, subject_suffix],
                outputs=[subjects_df]
            )

            delete_subject_btn.click(
                delete_subject,
                inputs=[subject_name],
                outputs=[subjects_df]
            )

            import_subjects_btn.click(
                import_subjects,
                inputs=[gr.File()],
                outputs=[subjects_df]
            )

            export_subjects_btn.click(
                export_subjects,
                outputs=[gr.Textbox()]
            )

            def delete_selected_row(df, evt: gr.SelectData):
                return df.drop(index=evt.index).reset_index(drop=True)

            delete_row_btn.click(
                delete_selected_row,
                inputs=[subjects_df],
                outputs=[subjects_df]
            )

            # Load initial subjects
            subjects_df.value = subject_manager.get_subjects_dataframe()

        with gr.TabItem("🎵 Music Lab"):
            # Project Context
            with gr.Accordion("Project Context 🎭", open=True):
                concept_input = gr.Textbox(
                    label="Concept",
                    placeholder="Describe your initial idea or concept for the music video...",
                    lines=5
                )
                genre_input = gr.Textbox(
                    label="Genre",
                    placeholder="Enter the genre of the music...",
                    info="Examples: Rock, Pop, Hip Hop, Electronic, Jazz, Metal, Indie Rock, Synth Pop, Alternative Hip Hop"
                )
                descriptors_input = gr.Textbox(
                    label="Descriptors",
                    placeholder="Enter descriptors for the music...",
                    info="Examples: Energetic, Melancholic, Political, Love, Falsetto, Guitar-driven, Synthesizer, Lo-fi, Catchy"
                )
            # Lyrics and Transcription
            with gr.Accordion("Lyrics Input 📝", open=True):
                lyrics_textbox = gr.Textbox(
                    label="Lyrics",
                    placeholder="Enter lyrics here or transcribe from an MP3 file...",
                    lines=10
                )
                with gr.Row():
                    audio_upload = gr.File(label="Upload MP3", file_types=[".mp3"])
                    include_timestamps = gr.Checkbox(label="Include Timestamps", value=False)
                    transcribe_button = gr.Button("Transcribe 🎙️")
                transcribe_button.click(
                    transcribe_audio_wrapper,
                    inputs=[audio_upload, include_timestamps],
                    outputs=lyrics_textbox
                )
                with gr.Row():
                    find_text = gr.Textbox(label="Find", scale=2)
                    replace_text = gr.Textbox(label="Replace", scale=2)
                    replace_button = gr.Button("Replace")
                def search_and_replace_lyrics(lyrics, find, replace):
                    return lyrics.replace(find, replace)

                replace_button.click(
                    search_and_replace_lyrics,
                    inputs=[lyrics_textbox, find_text, replace_text],
                    outputs=lyrics_textbox
                )
        
            # Music Player
            with gr.Accordion("Music Player 🎧", open=True):
                audio_player = gr.Audio(label="Play Uploaded MP3", type="filepath")
            
                def update_audio_player(file):
                    if file is not None:
                        return file.name
                    return None
            
                audio_upload.change(
                    update_audio_player,
                    inputs=[audio_upload],
                    outputs=[audio_player]
                )

            # Director's Assistant Chat Interface
            with gr.Accordion("Director's Assistant 🎬", open=False):
                chatbot = gr.Chatbot()
                chat_history = gr.State([])
                user_input = gr.Textbox(label="Your Message", placeholder="Type your message here...")
                send_button = gr.Button("Send")

                # Handle send button click
                async def on_send(user_input, concept, genre, descriptors, lyrics, chat_history):
                    if user_input.strip() == "":
                        return chat_history, chat_history, gr.update(value="")
                
                    updated_history, new_state = await handle_conversation(
                        user_input, concept, genre, descriptors, lyrics, chat_history
                    )
                    return updated_history, new_state, gr.update(value="")

                send_button.click(
                    on_send,
                    inputs=[user_input, concept_input, genre_input, descriptors_input, lyrics_textbox, chat_history],
                    outputs=[chatbot, chat_history, user_input],
                )

            # Video Treatment Generation
            with gr.Accordion("Video Treatment Generation 📽️", open=False):
                generate_treatment_button = gr.Button("Generate Video Treatment")
                video_treatment_output = gr.Textbox(label="Generated Video Treatment", lines=10)

                async def generate_treatment(concept, genre, descriptors, lyrics, chat_history):
                    project_context = {
                        "concept": concept,
                        "genre": genre,
                        "descriptors": descriptors,
                        "lyrics": lyrics
                    }
                    chat_history_str = "\n".join([f"{speaker}: {message}" for speaker, message in chat_history])
                    treatment = await director_assistant.generate_video_treatment(chat_history_str, project_context)
                    return treatment

                generate_treatment_button.click(
                    lambda *args: asyncio.run(generate_treatment(*args)),
                    inputs=[concept_input, genre_input, descriptors_input, lyrics_textbox, chat_history],
                    outputs=video_treatment_output
                )

            # Shot List Generation
            with gr.Accordion("Shot List Generation 🎥", open=False):
                generate_shot_list_button = gr.Button("Generate Shot List")
                shot_list_output = gr.Dataframe(
                    headers=["Scene", "Shot", "Description", "Notes"],
                    datatype=["str", "str", "str", "str"],
                    row_count=10,
                    col_count=(4, "fixed"),
                )

                # Character Management
                with gr.Row():
                    character_name = gr.Textbox(label="Character Name")
                    character_description = gr.Textbox(label="Character Description")
                    add_character_button = gr.Button("Add Character")

                characters_df = gr.Dataframe(
                    headers=["Name", "Description"],
                    datatype=["str", "str"],
                    row_count=5,
                    col_count=(2, "fixed"),
                )

                def add_character(name, description, current_df):
                    new_row = pd.DataFrame([[name, description]], columns=["Name", "Description"])
                    updated_df = pd.concat([current_df, new_row], ignore_index=True)
                    return updated_df

                add_character_button.click(
                    add_character,
                    inputs=[character_name, character_description, characters_df],
                    outputs=[characters_df]
                )

                generate_shot_list_button.click(
                    lambda *args: asyncio.run(generate_shot_list(*args)),
                    inputs=[concept_input, genre_input, descriptors_input, lyrics_textbox, chat_history, video_treatment_output, characters_df],
                    outputs=shot_list_output
                )

        with gr.TabItem("📜 Script Management"):
            with gr.Accordion("🎬 Proposed Shot List", open=True):
                # State to store the full DataFrame
                full_df = gr.State()

                column_view = gr.Radio(
                    choices=["Simple View", "Detailed View"],
                    value="Simple View",
                    label="Shot List View"
                )
                shot_list_df = gr.DataFrame(
                    headers=["Timestamp", "Scene", "Shot", "Reference", "Shot Description", "Shot Size", "People", "Places"],
                    label="Proposed Shot List",
                    interactive=False  # Set to True if you want it editable
                )
                generate_shot_list_btn = gr.Button("🎥 Generate Shot List")

            with gr.Row():
                save_shot_list_btn = gr.Button("💾 Save Shot List")
                export_shot_list_btn = gr.Button("📤 Export Shot List")
    
            with gr.Row():
                shot_list_notes = gr.Textbox(label="Shot List Notes", placeholder="Add any additional notes about the shot list here...")

            with gr.Accordion("👥 Proposed Subjects", open=True):
                subjects_df = gr.DataFrame(
                    headers=["Name", "Description", "Type"],
                    datatype=["str", "str", "str"],
                    col_count=(3, "fixed"),
                    label="Proposed Subjects",
                    interactive=True
                )
                extract_subjects_btn = gr.Button("🔍 Extract Subjects")
    
                with gr.Row():
                    subject_name_input = gr.Textbox(label="Subject Name")
                    subject_description_input = gr.Textbox(label="Subject Description")
                    subject_type_input = gr.Dropdown(label="Subject Type", choices=["person", "place", "prop"])
    
                with gr.Row():
                    add_subject_btn = gr.Button("➕ Add Subject")
                    update_subject_btn = gr.Button("🔄 Update Subject")
                    delete_subject_btn = gr.Button("🗑️ Delete Subject")
    
                send_to_subject_management_btn = gr.Button("📤 Send All to Subject Management")
                export_proposed_subjects_btn = gr.Button("💾 Export Proposed Subjects")

        with gr.Accordion("System Feedback", open=False):
            feedback_box = gr.Textbox(label="Feedback", interactive=False, lines=3)

            def update_shot_list_view(df, view_option):
                if df is None or df.empty:
                    return None
    
                required_columns = ["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"]
    
                # Ensure all required columns exist
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = ""
    
                if view_option == "Simple View":
                    return df[["Scene", "Shot Description", "Shot Size", "People"]]
                else:  # Detailed View
                    return df[required_columns]

            column_view.change(
                update_shot_list_view,
                inputs=[shot_list_df, column_view],
                outputs=[shot_list_df]
            )

    # Event handlers (placeholder functions for now)
    def save_style():
        return "Style saved"

    def delete_style():
        return "Style deleted"

    import random

    def create_random_style():
        adjectives = ["Vibrant", "Moody", "Retro", "Futuristic", "Ethereal", "Gritty", "Surreal", "Minimalist"]
        nouns = ["Watercolor", "Neon", "Cyberpunk", "Impressionist", "Abstract", "Pop Art", "Noir", "Steampunk"]
    
        style_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    
        prefix_templates = ["A {style} image of", "In the style of {style}:", "Reimagined as {style}:"]
        prefix = random.choice(prefix_templates).format(style=style_name)
    
        characteristics = ["high contrast", "soft focus", "vivid colors", "dramatic lighting", "muted tones", "sharp details", "dreamy atmosphere", "bold outlines"]
        suffix = "; ".join(random.sample(characteristics, random.randint(2, 4)))
    
        genres = ["Fantasy", "Sci-Fi", "Romance", "Horror", "Documentary", "Action", "Drama", "Comedy"]
        genre = random.choice(genres)
    
        descriptor_categories = {
            "Color": ["saturated", "monochromatic", "pastel", "neon", "earthy"],
            "Texture": ["smooth", "grainy", "glossy", "rough", "metallic"],
            "Mood": ["serene", "intense", "whimsical", "melancholic", "energetic"],
            "Technique": ["brush strokes", "digital art", "photorealistic", "collage", "vector graphics"]
        }
    
        descriptors = [random.choice(category) for category in descriptor_categories.values()]
        descriptors_str = "; ".join(descriptors)
    
        return {
            "Style Name": style_name,
            "Prefix": prefix,
            "Suffix": suffix,
            "Genre": genre,
            "Descriptors": descriptors_str
        }

    def generate_random_style():
        new_style = create_random_style()
        style_manager.add_style(new_style)
        return f"Generated new style: {new_style['Style Name']}", gr.update(choices=style_manager.get_styles())

    def generate_style_details():
        return "Style details generated"

    def copy_to_clipboard(text):
        return f"Copied to clipboard: {text}"

    def send_prompts():
        return "Prompts sent"

    # Connect event handlers
    save_style_btn.click(save_style)
    delete_style_btn.click(delete_style)
    random_style_btn.click(generate_random_style)
    generate_style_details_btn.click(generate_style_details)
    copy_concise_btn.click(lambda: copy_to_clipboard(concise_prompt.value))
    copy_normal_btn.click(lambda: copy_to_clipboard(normal_prompt.value))
    copy_detailed_btn.click(lambda: copy_to_clipboard(detailed_prompt.value))
    send_prompts_btn.click(send_prompts)

    # Script Management event handlers
    async def generate_proposed_shot_list(full_script, view_option):
        response = await script_manager.generate_proposed_shot_list(full_script)
        if isinstance(response, pd.DataFrame):
            df = response
        else:
            # Process the response and convert it to a DataFrame
            shots = [shot.split('|') for shot in response.split('\n') if shot.strip()]
            df = pd.DataFrame(shots, columns=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"])

        # Ensure all necessary columns exist
        required_columns = ["Timestamp", "Scene", "Shot", "Reference", "Shot Description", "Shot Size", "People", "Places"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        # Reset shot numbers for each scene
        def reset_shot_numbers(df):
            shot_number = 1
            current_scene = df.iloc[0]["Scene"]
            for i, row in df.iterrows():
                if row["Scene"] != current_scene:
                    shot_number = 1
                    current_scene = row["Scene"]
                df.at[i, "Shot"] = shot_number
                shot_number += 1
            return df

        # Apply the reset_shot_numbers function
        df = reset_shot_numbers(df)

        feedback = "Shot list generated successfully with shot numbers reset for each scene."
        return df, update_shot_list_view(df, view_option), feedback

    def save_proposed_shot_list():
        script_manager.save_proposed_shot_list("proposed_shot_list.csv")
        return "Proposed shot list saved to proposed_shot_list.csv"

    async def extract_proposed_subjects(full_script, shot_list):
        try:
            subjects_dict = await script_manager.extract_proposed_subjects(full_script, shot_list)
            subjects_df = pd.DataFrame(subjects_dict['subjects'])
            feedback = "Subjects extracted successfully."
            return subjects_df, feedback
        except Exception as e:
            error_message = f"Error extracting subjects: {str(e)}"
            print(error_message)
            return pd.DataFrame(columns=["Name", "Description", "Type"]), error_message

    def add_proposed_subject(name, description, subject_type, current_df):
        new_subject = pd.DataFrame([[name, description, subject_type]], columns=["Name", "Description", "Type"])
        updated_df = script_manager.merge_subjects(current_df, new_subject)
        return updated_df

    def update_proposed_subject(df, name, description, subject_type):
        updated_subject = pd.DataFrame([[name, description, subject_type]], columns=["Name", "Description", "Type"])
        return script_manager.merge_subjects(df, updated_subject)

    def delete_proposed_subject(df, name):
        return df[df['Name'] != name].reset_index(drop=True)

    def send_to_subject_management(proposed_subjects_df):
        # This function will be implemented in the Subject Management tab
        # For now, we'll just return a success message
        return "All subjects sent to Subject Management successfully."

    generate_shot_list_btn.click(
        generate_proposed_shot_list,
        inputs=[full_script_input, column_view],
        outputs=[full_df, shot_list_df, feedback_box]
    )

    extract_subjects_btn.click(
        extract_proposed_subjects,
        inputs=[full_script_input, shot_list_df],
        outputs=[subjects_df, feedback_box]
    )

    add_subject_btn.click(
        add_proposed_subject,
        inputs=[subject_name_input, subject_description_input, subject_type_input, subjects_df],
        outputs=[subjects_df]
    )

    update_subject_btn.click(
        update_proposed_subject,
        inputs=[subjects_df, subject_name_input, subject_description_input, subject_type_input],
        outputs=[subjects_df]
    )

    delete_subject_btn.click(
        delete_proposed_subject,
        inputs=[subjects_df, subject_name_input],
        outputs=[subjects_df]
    )

    def populate_subject_fields(evt: gr.SelectData, df):
        if evt.index is not None:
            row = df.iloc[evt.index[0]]
            return row['Name'], row['Description'], row['Type']
        return "", "", ""

    subjects_df.select(
        populate_subject_fields,
        inputs=[subjects_df],
        outputs=[subject_name_input, subject_description_input, subject_type_input]
    )

    send_to_subject_management_btn.click(
        send_to_subject_management,
        inputs=[subjects_df],
        outputs=[feedback_box]
    )

    export_proposed_subjects_btn.click(
        lambda df: script_manager.export_proposed_subjects(df, "proposed_subjects.csv"),
        inputs=[subjects_df],
        outputs=[feedback_box]
    )

    def send_to_directors_clipboard(text, current_clipboard):
        if current_clipboard:
            return current_clipboard + "\n\n" + text
        return text

    def clear_directors_clipboard():
        return ""

    def export_directors_clipboard(text):
        return gr.File.update(value=text.encode(), visible=True, filename="directors_clipboard.txt")

    def import_directors_clipboard(file):
        if file is not None:
            content = file.decode('utf-8')
            return content
        return ""

    copy_full_script_btn.click(
        send_to_directors_clipboard,
        inputs=[full_script_input, directors_clipboard],
        outputs=[directors_clipboard]
    )

    copy_concise_btn.click(
        send_to_directors_clipboard,
        inputs=[concise_prompt, directors_clipboard],
        outputs=[directors_clipboard]
    )

    copy_normal_btn.click(
        send_to_directors_clipboard,
        inputs=[normal_prompt, directors_clipboard],
        outputs=[directors_clipboard]
    )

    copy_detailed_btn.click(
        send_to_directors_clipboard,
        inputs=[detailed_prompt, directors_clipboard],
        outputs=[directors_clipboard]
    )

    def send_all_prompts(concise, normal, detailed, current_clipboard):
        all_prompts = f"Concise:\n{concise}\n\nNormal:\n{normal}\n\nDetailed:\n{detailed}"
        if current_clipboard:
            return current_clipboard + "\n\n" + all_prompts
        return all_prompts

    send_all_prompts_btn.click(
        send_all_prompts,
        inputs=[concise_prompt, normal_prompt, detailed_prompt, directors_clipboard],
        outputs=[directors_clipboard]
    )

    clear_clipboard_btn.click(
        clear_directors_clipboard,
        outputs=[directors_clipboard]
    )

    export_clipboard_btn.click(
        export_directors_clipboard,
        inputs=[directors_clipboard],
        outputs=[gr.File(label="Download Clipboard", visible=False)]
    )

    import_prompts_btn.click(
        import_prompts_from_file,
        inputs=[gr.File(label="Import Prompts from File")],
        outputs=[directors_clipboard]
    )

    def create_camera_settings():
        return {
            k: v for k, v in {
                "shot": shot.value,
                "move": move.value,
                "size": size.value,
                "framing": framing.value,
                "depth_of_field": depth_of_field.value,
                "camera_type": camera_type.value,
                "camera_name": camera_name.value,
                "lens_type": lens_type.value
            }.items() if v != "AI Suggest"
        }

    async def generate_prompts_wrapper(
        shot_description, directors_notes, style, style_prefix, style_suffix,
        director_style, shot, move, size, framing, depth_of_field, camera_type,
        camera_name, lens_type, end_parameters, stick_to_script, highlighted_text,
        full_script, people, places, props
    ):
        active_subjects = people + places + props
        return await script_prompt_generator.generate_prompts(
            script_excerpt=full_script,
            shot_description=shot_description,
            directors_notes=directors_notes,
            style=style,
            style_prefix=style_prefix,
            style_suffix=style_suffix,
            director_style=director_style,
            shot=shot,
            move=move,
            size=size,
            framing=framing,
            depth_of_field=depth_of_field,
            camera_type=camera_type,
            camera_name=camera_name,
            lens_type=lens_type,
            end_parameters=end_parameters,
            stick_to_script=stick_to_script,
            highlighted_text=highlighted_text,
            full_script=full_script,
            active_subjects=active_subjects
        )

    generate_button.click(
        fn=generate_prompts_wrapper,
        inputs=[
            shot_description_input,
            directors_notes_input,
            style_input,
            style_prefix_input,
            style_suffix_input,
            director_style_input,
            shot,
            move,
            size,
            framing,
            depth_of_field,
            camera_type,
            camera_name,
            lens_type,
            end_parameters_input,
            stick_to_script_input,
            highlighted_text_input,
            full_script_input,
            people,
            places,
            props
        ],
        outputs=[
            concise_prompt,
            normal_prompt,
            detailed_prompt,
            structured_prompt,
            generation_message,
            active_subjects_display
        ]
    )

    def update_subject_checkboxes():
        return {
            people: gr.update(choices=subject_manager.get_people()),
            places: gr.update(choices=subject_manager.get_places()),
            props: gr.update(choices=subject_manager.get_props())
        }

    # Add this to your existing event handlers
    add_subject_btn.click(update_subject_checkboxes, outputs=[people, places, props])
    update_subject_btn.click(update_subject_checkboxes, outputs=[people, places, props])
    delete_subject_btn.click(update_subject_checkboxes, outputs=[people, places, props])

    def receive_proposed_subjects(_):
        try:
            # Get the current proposed subjects from the script_manager
            proposed_subjects_df = script_manager.get_proposed_subjects()
            if proposed_subjects_df.empty:
                return None, "No proposed subjects available."
        
            # Merge the proposed subjects with the existing subjects in the Subject Management tab
            existing_df = subject_manager.get_subjects_dataframe()
            updated_df = subject_manager.merge_subjects(existing_df, proposed_subjects_df)
            subject_manager.set_subjects(updated_df)
            return updated_df, "Subjects received and merged successfully."
        except Exception as e:
            error_message = f"Error receiving proposed subjects: {str(e)}"
            print(error_message)  # For console logging
            return None, error_message

    # Add this in the Subject Management tab section
    with gr.TabItem("👥 Subject Management"):
        # ... (existing code)
    
        receive_proposed_subjects_btn = gr.Button("Receive Proposed Subjects")
        receive_proposed_subjects_btn.click(
            receive_proposed_subjects,
            inputs=[gr.State(None)],  # Add a dummy input
            outputs=[subjects_df, feedback_box]
        )

        # Update the prompts display when loading a project
        load_project_btn.click(
            lambda prompts: update_prompts_display(prompts),
            inputs=[gr.State(lambda: generated_prompts)],
            outputs=[prompts_display]
        )

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()

# Add these imports at the top of the file
import json
import os
from datetime import datetime

# Add or update these functions at the end of the file

def save_project(project_name, full_script, shot_list, subjects):
    if not project_name:
        return "Please enter a project name.", None

    project_data = {
        "name": project_name,
        "full_script": full_script,
        "shot_list": shot_list.to_dict() if isinstance(shot_list, pd.DataFrame) else {},
        "subjects": subjects.to_dict() if isinstance(subjects, pd.DataFrame) else {},
        "last_modified": datetime.now().isoformat()
    }
    
    with open(f"{project_name}.json", "w") as f:
        json.dump(project_data, f)
    
    return f"Project '{project_name}' saved successfully.", list_projects()

def load_project(project_name):
    try:
        with open(f"{project_name}.json", "r") as f:
            project_data = json.load(f)
        
        full_script = project_data.get("full_script", "")
        shot_list = pd.DataFrame(project_data.get("shot_list", {}))
        subjects = pd.DataFrame(project_data.get("subjects", {}))
        prompts = project_data.get("prompts", [])
        director_style = project_data.get("director_style", "")
        style = project_data.get("style", "")
        style_prefix = project_data.get("style_prefix", "")
        style_suffix = project_data.get("style_suffix", "")
        
        # Update the global generated_prompts
        global generated_prompts
        generated_prompts = prompts
        
        return full_script, shot_list, subjects, prompts, director_style, style, style_prefix, style_suffix, project_data, f"Project '{project_name}' loaded successfully."
    except FileNotFoundError:
        return None, None, None, None, None, None, None, None, None, f"Project '{project_name}' not found."
    except json.JSONDecodeError:
        return None, None, None, None, None, None, None, None, None, f"Error reading project file for '{project_name}'. The file may be corrupted."

def delete_project(project_name):
    try:
        os.remove(f"{project_name}.json")
        return f"Project '{project_name}' deleted successfully.", list_projects()
    except FileNotFoundError:
        return f"Project '{project_name}' not found.", list_projects()

def list_projects():
    projects = []
    for file in os.listdir():
        if file.endswith(".json"):
            try:
                with open(file, "r") as f:
                    project_data = json.load(f)
                    projects.append({
                        "Project Name": project_data.get("name", "Unknown"),
                        "Last Modified": project_data.get("last_modified", "Unknown")
                    })
            except json.JSONDecodeError:
                print(f"Error reading project file: {file}")
    return pd.DataFrame(projects)

def export_prompts(prompts, project_name):
    if not project_name:
        return "Please enter a project name."
    with open(f"{project_name}_prompts.txt", "w") as f:
        for prompt in prompts:
            f.write(f"{prompt}\n\n")
    return f"Prompts exported to '{project_name}_prompts.txt'"

# Global variable to store generated prompts
generated_prompts = []

# Modify the generate_prompts_wrapper function to append prompts
async def generate_prompts_wrapper(
    shot_description, directors_notes, style, style_prefix, style_suffix,
    director_style, shot, move, size, framing, depth_of_field, camera_type,
    camera_name, lens_type, end_parameters, stick_to_script, highlighted_text,
    full_script, people, places, props
):
    active_subjects = people + places + props
    result = await script_prompt_generator.generate_prompts(
        script_excerpt=full_script,
        shot_description=shot_description,
        directors_notes=directors_notes,
        style=style,
        style_prefix=style_prefix,
        style_suffix=style_suffix,
        director_style=director_style,
        shot=shot,
        move=move,
        size=size,
        framing=framing,
        depth_of_field=depth_of_field,
        camera_type=camera_type,
        camera_name=camera_name,
        lens_type=lens_type,
        end_parameters=end_parameters,
        stick_to_script=stick_to_script,
        highlighted_text=highlighted_text,
        full_script=full_script,
        active_subjects=active_subjects
    )
    
    # Append generated prompts to the global list
    generated_prompts.extend([result["concise"], result["normal"], result["detailed"]])
    
    return result["concise"], result["normal"], result["detailed"], result["structured"], "Prompts generated and saved.", ", ".join(active_subjects)

# Add event handlers for project management buttons
save_project_btn.click(
    save_project,
    inputs=[project_name_input, full_script_input, shot_list_df, subjects_df],
    outputs=[feedback_box, projects_df]
)

load_project_btn.click(
    load_project,
    inputs=[project_name_input],
    outputs=[full_script_input, shot_list_df, subjects_df, feedback_box]
)

delete_project_btn.click(
    delete_project,
    inputs=[project_name_input],
    outputs=[feedback_box, projects_df]
)

export_prompts_btn.click(
    export_prompts,
    inputs=[gr.State(lambda: generated_prompts), project_name_input],
    outputs=[feedback_box]
)

# Add this to initialize the projects list when the app starts
demo.load(list_projects, outputs=[projects_df])

# Update the projects list after saving or deleting a project
save_project_btn.click(list_projects, outputs=[projects_df])
delete_project_btn.click(list_projects, outputs=[projects_df])

# Update the generate_prompts_wrapper function to store prompts globally
def generate_prompts_wrapper(*args, **kwargs):
    global generated_prompts
    result = asyncio.run(script_prompt_generator.generate_prompts(*args, **kwargs))
    generated_prompts.extend([result["concise"], result["normal"], result["detailed"]])
    return (result["concise"], result["normal"], result["detailed"], 
            result["structured"], "Prompts generated and saved.", ", ".join(kwargs.get('active_subjects', [])))

# Connect the generate_prompts_wrapper to the generate_button
generate_button.click(
    fn=generate_prompts_wrapper,
    inputs=[
        shot_description_input,
        directors_notes_input,
        style_input,
        style_prefix_input,
        style_suffix_input,
        director_style_input,
        shot,
        move,
        size,
        framing,
        depth_of_field,
        camera_type,
        camera_name,
        lens_type,
        end_parameters_input,
        stick_to_script_input,
        highlighted_text_input,
        full_script_input,
        people,
        places,
        props
    ],
    outputs=[
        concise_prompt,
        normal_prompt,
        detailed_prompt,
        structured_prompt,
        generation_message,
        active_subjects_display
    ]
)
