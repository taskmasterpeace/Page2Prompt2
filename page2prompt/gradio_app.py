import sys
import os
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

    async def generate_prompts_with_end_params(*args):
        # Separate end_parameters from other arguments
        end_parameters = args[8]
        other_args = args[:8] + args[9:]
        
        # Call the original generate_prompts method
        results = await script_prompt_generator.generate_prompts(*other_args)
        
        # Append end_parameters to each prompt
        updated_results = list(results)
        for i in range(4):  # Update the first 4 outputs (prompts)
            if updated_results[i]:
                updated_results[i] = f"{updated_results[i]} {end_parameters}"
        
        return tuple(updated_results)

    generate_button.click(
        fn=generate_prompts_with_end_params,
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
