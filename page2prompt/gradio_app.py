import gradio as gr
import asyncio
import csv
import os
import pandas as pd
import json
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
director_assistant = DirectorAssistant(meta_chain)
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
        director_style_input = gr.Dropdown(label="🎬 Director Style", choices=[style['name'] for style in director_styles])
        with gr.Accordion("📜 Full Script", open=False):
            with gr.Row():
                full_script_input = gr.Textbox(label="📚 Full Script", lines=10)
                copy_full_script_btn = gr.Button("📋", scale=1)

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
                            copy_concise_btn = gr.Button("📋", scale=1)
                        with gr.Row():
                            normal_prompt = gr.Textbox(label="Normal")
                            copy_normal_btn = gr.Button("📋", scale=1)
                        with gr.Row():
                            detailed_prompt = gr.Textbox(label="Detailed")
                            copy_detailed_btn = gr.Button("📋", scale=1)
                        
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
            
            with gr.Row():
                add_subject_btn = gr.Button("Add Subject")
                update_subject_btn = gr.Button("Update Subject")
                delete_subject_btn = gr.Button("Delete Subject")
                import_subjects_btn = gr.Button("Import Subjects")
                export_subjects_btn = gr.Button("Export Subjects")

            subjects_df = gr.DataFrame(
                headers=["Name", "Description", "Alias", "Type", "Prefix", "Suffix", "Active"],
                datatype=["str", "str", "str", "str", "str", "str", "bool"],
                col_count=(7, "fixed"),
                interactive=True
            )

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
                column_view = gr.Radio(
                    choices=["Simple View", "Detailed View"],
                    value="Simple View",
                    label="Shot List View"
                )
                shot_list_df = gr.DataFrame(
                    headers=["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"],
                    label="Proposed Shot List",
                    interactive=True
                )
                generate_shot_list_btn = gr.Button("🎥 Generate Shot List")

            with gr.Row():
                save_shot_list_btn = gr.Button("💾 Save Shot List")
                export_shot_list_btn = gr.Button("📤 Export Shot List")
        
            with gr.Row():
                shot_list_notes = gr.Textbox(label="Shot List Notes", placeholder="Add any additional notes about the shot list here...")
                shot_list_feedback = gr.Textbox(label="Feedback", placeholder="System feedback will appear here", interactive=False)

            with gr.Accordion("👥 Proposed Subjects", open=True):
                subjects_df = gr.DataFrame(
                    headers=["name", "description", "type"],
                    datatype=["str", "str", "str"],
                    col_count=(3, "fixed"),
                    label="Proposed Subjects",
                    interactive=False
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
            
                send_to_subject_management_btn = gr.Button("📤 Send to Subject Management")
                export_proposed_subjects_btn = gr.Button("💾 Export Proposed Subjects")

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
        required_columns = ["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""

        # Ensure "Shot" column is filled
        df["Shot"] = df.index + 1  # Assuming each row is a separate shot

        feedback = "Shot list generated successfully."
        return update_shot_list_view(df, view_option), feedback

    def save_proposed_shot_list():
        script_manager.save_proposed_shot_list("proposed_shot_list.csv")
        return "Proposed shot list saved to proposed_shot_list.csv"

    async def extract_proposed_subjects(full_script):
        return await script_manager.extract_proposed_subjects(full_script)

    def add_proposed_subject(name, description, subject_type):
        script_manager.add_proposed_subject(name, description, subject_type)
        return script_manager.get_proposed_subjects()

    async def extract_proposed_subjects(full_script):
        try:
            subjects_df = await script_manager.extract_proposed_subjects(full_script)
            feedback = "Subjects extracted successfully."
            return subjects_df, feedback
        except Exception as e:
            error_message = f"Error extracting subjects: {str(e)}"
            print(error_message)
            return None, error_message

    def update_shot_list_view(df, view_option):
        if df is None or df.empty:
            return None
        all_columns = ["Timestamp", "Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People", "Places"]
        simple_columns = ["Scene", "Shot Description", "Shot Size", "People"]
        visible_columns = simple_columns if view_option == "Simple View" else all_columns

        # Ensure all columns exist in the DataFrame
        for col in all_columns:
            if col not in df.columns:
                df[col] = ""

        # Filter the DataFrame based on the selected view
        filtered_df = df[visible_columns]

        return gr.DataFrame.update(value=filtered_df)

    generate_shot_list_btn.click(
        generate_proposed_shot_list,
        inputs=[full_script_input, column_view],
        outputs=[shot_list_df, shot_list_feedback]
    )

    extract_subjects_btn.click(
        extract_proposed_subjects,
        inputs=[full_script_input],
        outputs=[subjects_df, shot_list_feedback]
    )

    column_view.change(
        update_shot_list_view,
        inputs=[shot_list_df, column_view],
        outputs=[shot_list_df]
    )

    # Add these event handlers for subject management
    def add_subject(name, description, subject_type):
        new_subject = pd.DataFrame([[name, description, subject_type]], columns=["name", "description", "type"])
        updated_df = pd.concat([subjects_df.value, new_subject], ignore_index=True)
        return updated_df

    def update_subject(df, name, description, subject_type):
        selected_index = df.index[df['name'] == name].tolist()
        if selected_index:
            index = selected_index[0]
            df.loc[index] = [name, description, subject_type]
        return df

    def delete_subject(df, name):
        return df[df['name'] != name].reset_index(drop=True)

    add_subject_btn.click(
        add_subject,
        inputs=[subject_name_input, subject_description_input, subject_type_input],
        outputs=[subjects_df]
    )

    update_subject_btn.click(
        update_subject,
        inputs=[subjects_df, subject_name_input, subject_description_input, subject_type_input],
        outputs=[subjects_df]
    )

    delete_subject_btn.click(
        delete_subject,
        inputs=[subjects_df, subject_name_input],
        outputs=[subjects_df]
    )

    def populate_subject_fields(evt: gr.SelectData, df):
        if evt.index is not None:
            row = df.iloc[evt.index[0]]
            return row['name'], row['description'], row['type']
        return "", "", ""

    subjects_df.select(
        populate_subject_fields,
        inputs=[subjects_df],
        outputs=[subject_name_input, subject_description_input, subject_type_input]
    )

    send_to_subject_management_btn.click(
        lambda df: script_manager.send_to_subject_management(df),
        inputs=[subjects_df],
        outputs=[shot_list_feedback]
    )

    export_proposed_subjects_btn.click(
        lambda df: script_manager.export_proposed_subjects(df, "proposed_subjects.csv"),
        inputs=[subjects_df],
        outputs=[shot_list_feedback]
    )

    def copy_to_clipboard(text):
        return text

    copy_full_script_btn.click(
        copy_to_clipboard,
        inputs=[full_script_input],
        outputs=[gr.Textbox(visible=False)]
    )

    copy_concise_btn.click(
        copy_to_clipboard,
        inputs=[concise_prompt],
        outputs=[gr.Textbox(visible=False)]
    )

    copy_normal_btn.click(
        copy_to_clipboard,
        inputs=[normal_prompt],
        outputs=[gr.Textbox(visible=False)]
    )

    copy_detailed_btn.click(
        copy_to_clipboard,
        inputs=[detailed_prompt],
        outputs=[gr.Textbox(visible=False)]
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

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()
