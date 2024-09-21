import gradio as gr
import asyncio
import csv
import os
import pandas as pd
from page2prompt.components.script_prompt_generation import ScriptPromptGenerator
from page2prompt.utils.subject_manager import SubjectManager
from page2prompt.utils.style_manager import StyleManager
from page2prompt.components.meta_chain import MetaChain
from page2prompt.utils.shot_list_generator import generate_shot_list

# Initialize components
style_manager = StyleManager("styles.csv")
subject_manager = SubjectManager("subjects.csv")
meta_chain = MetaChain()
script_prompt_generator = ScriptPromptGenerator(style_manager, subject_manager, meta_chain)

# Load camera settings from CSV
def load_camera_settings(csv_file):
    settings = {}
    file_path = os.path.join(os.path.dirname(__file__), csv_file)
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['type'] not in settings:
                settings[row['type']] = []
            settings[row['type']].append(row['display'])
    return settings

camera_settings = load_camera_settings("camera_settings.csv")

# Load director styles from CSV
def load_director_styles(csv_file):
    styles = []
    file_path = os.path.join(os.path.dirname(__file__), csv_file)
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        styles = list(reader)
    return styles

director_styles = load_director_styles("director_styles.csv")

# Transcribe audio function
def transcribe_audio(audio_file, include_timestamps):
    # Placeholder function for audio transcription
    # You should implement the actual transcription logic here
    return f"Transcribed text from {audio_file.name}" + (" with timestamps" if include_timestamps else "")

# Gradio interface setup
with gr.Blocks() as demo:
    with gr.Accordion("🎬 Script & Director Style", open=True):
        director_style_input = gr.Dropdown(label="🎬 Director Style", choices=[style['name'] for style in director_styles])
        full_script_input = gr.Textbox(label="📚 Full Script", lines=5)

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
                                people_places = gr.CheckboxGroup(label="People & Places", choices=["Person 1", "Person 2", "Place 1", "Place 2"])
                            with gr.Column():
                                animals_things = gr.CheckboxGroup(label="Animals & Things", choices=["Animal 1", "Animal 2", "Thing 1", "Thing 2"])

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
                            copy_concise_btn = gr.Button("📋")
                        with gr.Row():
                            normal_prompt = gr.Textbox(label="Normal")
                            copy_normal_btn = gr.Button("📋")
                        with gr.Row():
                            detailed_prompt = gr.Textbox(label="Detailed")
                            copy_detailed_btn = gr.Button("📋")
                        
                        structured_prompt = gr.Textbox(label="Structured Prompt")
                        generation_message = gr.Textbox(label="Generation Message")
                        active_subjects_display = gr.Textbox(label="Active Subjects")
                        
                        send_prompts_btn = gr.Button("📤 Send Prompts")

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
                    transcribe_audio,
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

    # Event handlers (placeholder functions for now)
    def save_style():
        return "Style saved"

    def delete_style():
        return "Style deleted"

    def generate_random_style():
        return "Random style generated"

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

    generate_button.click(
        fn=lambda *args: asyncio.run(script_prompt_generator.generate_prompts(*args)),
        inputs=[
            full_script_input,
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

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()
import gradio as gr
import asyncio
from page2prompt.components.script_prompt_generation import ScriptPromptGenerator
from page2prompt.utils.subject_manager import SubjectManager
from page2prompt.utils.style_manager import StyleManager
from page2prompt.components.meta_chain import MetaChain

# Initialize components
style_manager = StyleManager("styles.csv")
subject_manager = SubjectManager("subjects.csv")
meta_chain = MetaChain()
script_prompt_generator = ScriptPromptGenerator(style_manager, subject_manager, meta_chain)

# Gradio interface setup
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            script_input = gr.Textbox(label="Script Excerpt")
            shot_description_input = gr.Textbox(label="Shot Description")
            directors_notes_input = gr.Textbox(label="Director's Notes")
            style_input = gr.Dropdown(label="Style", choices=style_manager.get_styles())
            style_prefix_input = gr.Textbox(label="Style Prefix")
            style_suffix_input = gr.Textbox(label="Style Suffix")
            director_style_input = gr.Textbox(label="Director's Style")
            stick_to_script_input = gr.Checkbox(label="Stick to Script")
            highlighted_text_input = gr.Textbox(label="Highlighted Text")
            full_script_input = gr.Textbox(label="Full Script")
            end_parameters_input = gr.Textbox(label="End Parameters")

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

        with gr.Column():
            concise_prompt = gr.Textbox(label="Concise Prompt")
            normal_prompt = gr.Textbox(label="Normal Prompt")
            detailed_prompt = gr.Textbox(label="Detailed Prompt")
            structured_prompt = gr.Textbox(label="Structured Prompt")
            generation_message = gr.Textbox(label="Generation Message")
            active_subjects_display = gr.Textbox(label="Active Subjects")

    generate_button = gr.Button("Generate Prompts")

    generate_button.click(
        fn=lambda *args: asyncio.run(script_prompt_generator.generate_prompts(*args)),
        inputs=[
            script_input,
            shot_description_input,
            directors_notes_input,
            style_input,
            style_prefix_input,
            style_suffix_input,
            director_style_input,
            gr.JSON({
                "shot": lambda: shot.value,
                "move": lambda: move.value,
                "size": lambda: size.value,
                "framing": lambda: framing.value,
                "depth_of_field": lambda: depth_of_field.value,
                "camera_type": lambda: camera_type.value,
                "camera_name": lambda: camera_name.value,
                "lens_type": lambda: lens_type.value
            }),
            end_parameters_input,
            stick_to_script_input,
            highlighted_text_input,
            full_script_input,
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

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()
