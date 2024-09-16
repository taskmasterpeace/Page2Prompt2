import sys
import os
import csv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

            with gr.Box():
                gr.Markdown("### Camera Settings")
                shot_size = gr.Dropdown(label="Shot Size", choices=camera_settings.get('size', []))
                shot_movement = gr.Dropdown(label="Shot Movement", choices=camera_settings.get('move', []))
                framing = gr.Dropdown(label="Framing", choices=camera_settings.get('framing', []))
                depth_of_field = gr.Dropdown(label="Depth of Field", choices=camera_settings.get('depth_of_field', []))
                camera_type = gr.Dropdown(label="Camera Type", choices=camera_settings.get('camera_type', []))
                camera_name = gr.Dropdown(label="Camera Name", choices=camera_settings.get('camera_name', []))
                lens_type = gr.Dropdown(label="Lens Type", choices=camera_settings.get('lens_type', []))

        with gr.Column():
            concise_prompt = gr.Textbox(label="Concise Prompt")
            normal_prompt = gr.Textbox(label="Normal Prompt")
            detailed_prompt = gr.Textbox(label="Detailed Prompt")
            structured_prompt = gr.Textbox(label="Structured Prompt")
            generation_message = gr.Textbox(label="Generation Message")
            active_subjects_display = gr.Textbox(label="Active Subjects")

    generate_button = gr.Button("Generate Prompts")

    def prepare_camera_settings(*args):
        return {
            "size": args[0],
            "move": args[1],
            "framing": args[2],
            "depth_of_field": args[3],
            "camera_type": args[4],
            "camera_name": args[5],
            "lens_type": args[6]
        }

    generate_button.click(
        fn=lambda *args: asyncio.run(script_prompt_generator.generate_prompts(*args[:8], prepare_camera_settings(*args[8:15]), *args[15:])),
        inputs=[
            script_input,
            shot_description_input,
            directors_notes_input,
            style_input,
            style_prefix_input,
            style_suffix_input,
            director_style_input,
            end_parameters_input,
            shot_size,
            shot_movement,
            framing,
            depth_of_field,
            camera_type,
            camera_name,
            lens_type,
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

            camera_settings_input = gr.JSON(label="Camera Settings", value={
                "shot": "Medium",
                "move": "Static",
                "size": "Medium",
                "framing": "Center",
                "depth_of_field": "Medium"
            })

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
            camera_settings_input,
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
