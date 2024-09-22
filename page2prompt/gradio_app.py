import gradio as gr
import asyncio
import csv
import os
import pandas as pd
from page2prompt.components.script_prompt_generation import ScriptPromptGenerator
from page2prompt.utils.subject_manager import SubjectManager, Subject
from page2prompt.utils.style_manager import StyleManager
from page2prompt.components.meta_chain import MetaChain
from page2prompt.utils.shot_list_generator import generate_shot_list
from page2prompt.components.director_assistant import DirectorAssistant
from page2prompt.music_lab import transcribe_audio, search_and_replace_lyrics

# Initialize components
style_manager = StyleManager("styles.csv")
subject_manager = SubjectManager("subjects.csv")
meta_chain = MetaChain()
script_prompt_generator = ScriptPromptGenerator(style_manager, subject_manager, meta_chain)
director_assistant = DirectorAssistant(meta_chain)

async def handle_conversation(user_input, concept, genre, descriptors, lyrics, chat_history):
    # Placeholder function for handling conversation
    # You should implement the actual conversation logic here
    updated_history = chat_history + [("User", user_input), ("Assistant", "This is a placeholder response.")]
    return updated_history, updated_history

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
def transcribe_audio_wrapper(audio_file, include_timestamps):
    if audio_file is None:
        return "Please upload an MP3 file."
    return transcribe_audio(audio_file, include_timestamps)

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
