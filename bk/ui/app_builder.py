import gradio as gr
from page2prompt.ui.ui_components import create_master_tabs
from page2prompt.ui.event_handlers import (
    generate_prompts_handler,
    generate_bulk_notes_handler,
    generate_bulk_prompts_handler,
    save_project_handler,
    load_project_handler,
    delete_project_handler,
    add_subject_handler,
    update_subject_handler,
    delete_subject_handler,
    import_subjects_handler,
    export_subjects_handler,
    receive_proposed_subjects_handler,
    generate_random_style_handler,
    transcribe_audio_handler,
    search_and_replace_lyrics_handler
)

def create_gradio_app(config):
    with gr.Blocks() as demo:
        components = create_master_tabs(
            config.style_manager,
            config.director_assistant,
            config.subject_manager,
            config.project_manager
        )

        # Event handlers
        components['script_tab_components']['generate_button'].click(
            generate_prompts_handler,
            inputs=[
                components['script_tab_components']['shot_description_input'],
                components['script_tab_components']['directors_notes_input'],
                components['full_script_input'],
                components['script_tab_components']['style_input'],
                components['script_tab_components']['style_prefix_input'],
                components['script_tab_components']['style_suffix_input'],
                components['script_tab_components']['director_style_input'],
                components['script_tab_components'].get('people', gr.CheckboxGroup()),
                components['script_tab_components'].get('places', gr.CheckboxGroup()),
                components['script_tab_components'].get('props', gr.CheckboxGroup()),
                components['script_tab_components'].get('shot', gr.Dropdown()),
                components['script_tab_components'].get('move', gr.Dropdown()),
                components['script_tab_components'].get('size', gr.Dropdown()),
                components['script_tab_components'].get('framing', gr.Dropdown()),
                components['script_tab_components'].get('depth_of_field', gr.Dropdown()),
                components['script_tab_components'].get('camera_type', gr.Dropdown()),
                components['script_tab_components'].get('camera_name', gr.Dropdown()),
                components['script_tab_components'].get('lens_type', gr.Dropdown()),
                components['script_tab_components'].get('end_parameters_input', gr.Textbox()),
                gr.State(config.style_manager),
                gr.State(config.subject_manager),
            ],
            outputs=[
                components['script_tab_components']['concise_output'],
                components['script_tab_components']['normal_output'],
                components['script_tab_components']['detailed_output'],
                components['script_tab_components'].get('structured_output', gr.Textbox()),
                components['script_tab_components'].get('generation_message', gr.Textbox()),
                components['script_tab_components'].get('active_subjects_display', gr.Textbox())
            ]
        )

        components['bulk_prompt_tab_components']['generate_bulk_notes_btn'].click(
            generate_bulk_notes_handler,
            inputs=[gr.State(config.api_key), gr.State(config.subject_manager), gr.State(config.style_manager), gr.State(config.director_assistant)] + components['bulk_prompt_tab_components']['bulk_notes_inputs'],
            outputs=components['bulk_prompt_tab_components']['bulk_notes_outputs']
        )

        components['bulk_prompt_tab_components']['generate_bulk_prompts_btn'].click(
            generate_bulk_prompts_handler,
            inputs=[gr.State(config.api_key), gr.State(config.subject_manager), gr.State(config.style_manager), gr.State(config.director_assistant)] + components['bulk_prompt_tab_components']['bulk_prompts_inputs'],
            outputs=components['bulk_prompt_tab_components']['bulk_prompts_outputs']
        )

        components['project_tab_components']['save_project_btn'].click(
            save_project_handler,
            inputs=[gr.State(config.project_manager)] + components['project_tab_components']['save_inputs'],
            outputs=components['project_tab_components']['save_outputs']
        )

        components['project_tab_components']['load_project_btn'].click(
            load_project_handler,
            inputs=[gr.State(config.project_manager)] + components['project_tab_components']['load_inputs'],
            outputs=components['project_tab_components']['load_outputs']
        )

        components['project_tab_components']['delete_project_btn'].click(
            delete_project_handler,
            inputs=[gr.State(config.project_manager)] + components['project_tab_components']['delete_inputs'],
            outputs=components['project_tab_components']['delete_outputs']
        )

        components['subject_tab_components']['add_subject_btn'].click(
            add_subject_handler,
            inputs=[gr.State(config.subject_manager)] + components['subject_tab_components']['add_subject_inputs'],
            outputs=[components['subject_tab_components']['subjects_df']]
        )

        components['subject_tab_components']['update_subject_btn'].click(
            update_subject_handler,
            inputs=[gr.State(config.subject_manager)] + components['subject_tab_components']['update_subject_inputs'],
            outputs=[components['subject_tab_components']['subjects_df']]
        )

        components['subject_tab_components']['delete_subject_btn'].click(
            delete_subject_handler,
            inputs=[gr.State(config.subject_manager)] + components['subject_tab_components']['delete_subject_inputs'],
            outputs=[components['subject_tab_components']['subjects_df']]
        )

        components['subject_tab_components']['import_subjects_btn'].click(
            import_subjects_handler,
            inputs=[gr.State(config.subject_manager), components['subject_tab_components']['import_subjects_input']],
            outputs=[components['subject_tab_components']['subjects_df'], components['subject_tab_components']['feedback_box']]
        )

        components['subject_tab_components']['export_subjects_btn'].click(
            export_subjects_handler,
            inputs=[gr.State(config.subject_manager)],
            outputs=[components['subject_tab_components']['feedback_box']]
        )

        components['subject_tab_components']['receive_proposed_subjects_btn'].click(
            receive_proposed_subjects_handler,
            inputs=[gr.State(config.subject_manager), gr.State(config.script_manager)],
            outputs=[components['subject_tab_components']['subjects_df'], components['subject_tab_components']['feedback_box']]
        )

        components['script_tab_components']['random_style_btn'].click(
            generate_random_style_handler,
            inputs=[gr.State(config.style_manager)],
            outputs=[components['script_tab_components']['style_message'], components['script_tab_components']['style_input']]
        )

        components['music_lab_tab_components']['transcribe_button'].click(
            transcribe_audio_handler,
            inputs=[gr.State(config.audio_processor), components['music_lab_tab_components']['audio_upload'], components['music_lab_tab_components']['include_timestamps']],
            outputs=[components['music_lab_tab_components']['lyrics_textbox']]
        )

        components['music_lab_tab_components']['replace_button'].click(
            search_and_replace_lyrics_handler,
            inputs=[gr.State(config.audio_processor), components['music_lab_tab_components']['lyrics_textbox'], components['music_lab_tab_components']['find_text'], components['music_lab_tab_components']['replace_text']],
            outputs=[components['music_lab_tab_components']['lyrics_textbox']]
        )

    return demo
