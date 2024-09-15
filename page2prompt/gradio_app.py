import gradio as gr
from components.script_prompt_generation import ScriptPromptGenerator
from components.subject_management import SubjectManager
from utils.style_manager import StyleManager
from components.meta_chain import MetaChain

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
            director_style_input = gr.Textbox(label="Director's Style")
            stick_to_script_input = gr.Checkbox(label="Stick to Script")
            highlighted_text_input = gr.Textbox(label="Highlighted Text")
            full_script_input = gr.Textbox(label="Full Script")
            end_parameters_input = gr.Textbox(label="End Parameters")

            with gr.Row():
                camera_shot_input = gr.Dropdown(label="Camera Shot", choices=["Close-up", "Medium", "Wide"])
                camera_move_input = gr.Dropdown(label="Camera Move", choices=["Static", "Pan", "Tilt", "Dolly"])
                camera_size_input = gr.Dropdown(label="Camera Size", choices=["Small", "Medium", "Large"])
                framing_input = gr.Dropdown(label="Framing", choices=["Center", "Rule of Thirds", "Golden Ratio"])
                depth_of_field_input = gr.Dropdown(label="Depth of Field", choices=["Shallow", "Medium", "Deep"])

        with gr.Column():
            concise_prompt = gr.Textbox(label="Concise Prompt")
            normal_prompt = gr.Textbox(label="Normal Prompt")
            detailed_prompt = gr.Textbox(label="Detailed Prompt")
            structured_prompt = gr.Textbox(label="Structured Prompt")
            generation_message = gr.Textbox(label="Generation Message")
            active_subjects_display = gr.Textbox(label="Active Subjects")

    generate_button = gr.Button("Generate Prompts")

    generate_button.click(
        fn=lambda *args: script_prompt_generator.generate_prompts(*args),
        inputs=[
            script_input,
            shot_description_input,
            directors_notes_input,
            style_input,
            director_style_input,
            stick_to_script_input,
            highlighted_text_input,
            full_script_input,
            end_parameters_input,
            camera_shot_input,
            camera_move_input,
            camera_size_input,
            framing_input,
            depth_of_field_input,
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
