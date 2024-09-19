import gradio as gr
import asyncio
import csv
import os
from page2prompt.components.script_prompt_generation import ScriptPromptGenerator
from page2prompt.utils.subject_manager import SubjectManager
from page2prompt.utils.style_manager import StyleManager
from page2prompt.components.meta_chain import MetaChain

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
            gr.Markdown("Music Lab functionality will be implemented here.")

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
