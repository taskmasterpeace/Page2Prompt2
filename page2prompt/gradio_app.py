import gradio as gr
import asyncio
from components.script_prompt_generation import ScriptPromptGenerator
from components.subject_management import SubjectManager
from utils.style_manager import StyleManager
from components.meta_chain import MetaChain
from config import Config
from core import PromptForgeCore
from prompt_manager import PromptManager

# Initialize components
config = Config()
core = PromptForgeCore()
prompt_manager = PromptManager()
style_manager = StyleManager("styles.csv")
subject_manager = SubjectManager("subjects.csv")
meta_chain = MetaChain(core)
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
demo.launch()
import gradio as gr
from components.script_prompt_generation import ScriptPromptGenerator
from components.subject_management import SubjectManager
from utils.style_manager import StyleManager

# Initialize components
style_manager = StyleManager()
subject_manager = SubjectManager()
script_prompt_generator = ScriptPromptGenerator(style_manager, subject_manager)

# Gradio interface setup
def generate_prompts(script_excerpt, shot_description, directors_notes):
    # Placeholder function, to be implemented
    return "Placeholder prompt"

demo = gr.Interface(
    fn=generate_prompts,
    inputs=[
        gr.Textbox(label="Script Excerpt"),
        gr.Textbox(label="Shot Description"),
        gr.Textbox(label="Director's Notes")
    ],
    outputs=gr.Textbox(label="Generated Prompt")
)

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch()
