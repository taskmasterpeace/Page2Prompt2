import gradio as gr
from page2prompt.components.style_management import StyleManager
from page2prompt.api.subject_management import SubjectManager
from page2prompt.api.prompt_generation import PromptGenerator
from page2prompt.components.project_management import ProjectManager

def create_master_tabs(style_manager, director_assistant, subject_manager, project_manager):
    with gr.Tabs() as master_tabs:
        with gr.Tab("Script & Director Style"):
            with gr.Accordion("Full Script", open=False):
                full_script_input = gr.Textbox(label="Full Script", lines=10)
            
            with gr.Accordion("Master Shot List", open=True):
                master_shot_list_df = gr.DataFrame(
                    headers=["Timestamp", "Scene", "Shot", "Reference", "Shot Description", "Shot Size", "People", "Places"],
                    label="Master Shot List",
                    interactive=True
                )
            
            with gr.Tabs() as sub_tabs:
                with gr.TabItem("Shot and Prompt Generation"):
                    script_tab_components = create_script_tab(style_manager, director_assistant)
                
                with gr.TabItem("Subject Management"):
                    subject_tab_components = create_subject_management_tab(subject_manager)
                
                with gr.TabItem("Bulk Prompt Management"):
                    bulk_prompt_tab_components = create_bulk_prompt_management_tab(style_manager, director_assistant)
                
                with gr.TabItem("Project Management"):
                    project_tab_components = create_project_management_tab(project_manager)
        
        with gr.Tab("Music Lab"):
            music_lab_tab_components = create_music_lab_tab()
    
    return {
        "master_tabs": master_tabs,
        "full_script_input": full_script_input,
        "master_shot_list_df": master_shot_list_df,
        "script_tab_components": script_tab_components,
        "subject_tab_components": subject_tab_components,
        "bulk_prompt_tab_components": bulk_prompt_tab_components,
        "project_tab_components": project_tab_components,
        "music_lab_tab_components": music_lab_tab_components
    }

def create_script_tab(style_manager: StyleManager, director_assistant):
    with gr.Accordion("🎬 Script & Director Style", open=True):
        director_style_input = gr.Dropdown(label="🎬 Director Style", choices=["No Director"] + [style['name'] for style in director_assistant.get_director_styles()])
        with gr.Accordion("📜 Full Script", open=False):
            with gr.Row():
                full_script_input = gr.Textbox(label="📚 Full Script", lines=10)
                copy_full_script_btn = gr.Button("📋 Send to Clipboard", scale=1)
        
        shot_description_input = gr.Textbox(label="📸 Shot Description", lines=3)
        directors_notes_input = gr.Textbox(label="🎬 Director's Notes", lines=3)
        
        with gr.Row():
            style_input = gr.Dropdown(label="Style", choices=style_manager.get_styles(), interactive=True)
            style_prefix_input = gr.Textbox(label="Style Prefix", interactive=False)
            style_suffix_input = gr.Textbox(label="Style Suffix", interactive=False)
        
        random_style_btn = gr.Button("🎨 Generate Random Style")
        style_message = gr.Textbox(label="Style Message", interactive=False)
    
    generate_button = gr.Button("Generate Prompts")
    
    with gr.Row():
        concise_output = gr.Textbox(label="Concise Prompt", lines=3)
        normal_output = gr.Textbox(label="Normal Prompt", lines=5)
        detailed_output = gr.Textbox(label="Detailed Prompt", lines=7)

    return {
        "director_style_input": director_style_input,
        "full_script_input": full_script_input,
        "copy_full_script_btn": copy_full_script_btn,
        "shot_description_input": shot_description_input,
        "directors_notes_input": directors_notes_input,
        "generate_button": generate_button,
        "random_style_btn": random_style_btn,
        "style_message": style_message,
        "style_input": style_input,
        "style_prefix_input": style_prefix_input,
        "style_suffix_input": style_suffix_input,
        "concise_output": concise_output,
        "normal_output": normal_output,
        "detailed_output": detailed_output,
    }

def create_subject_management_tab(subject_manager: SubjectManager):
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

        return {
            "subject_name": subject_name,
            "subject_description": subject_description,
            "subject_alias": subject_alias,
            "subject_type": subject_type,
            "subject_prefix": subject_prefix,
            "subject_suffix": subject_suffix,
            "subjects_df": subjects_df,
            "add_subject_btn": add_subject_btn,
            "update_subject_btn": update_subject_btn,
        "delete_subject_btn": delete_subject_btn,
        "delete_row_btn": delete_row_btn,
        "import_subjects_btn": import_subjects_btn,
        "export_subjects_btn": export_subjects_btn,
        "receive_proposed_subjects_btn": receive_proposed_subjects_btn,
        "add_subject_inputs": [subject_name, subject_description, subject_alias, subject_type, subject_prefix, subject_suffix],
        "update_subject_inputs": [subject_name, subject_description, subject_alias, subject_type, subject_prefix, subject_suffix],
        "delete_subject_inputs": [subject_name],
        "import_subjects_input": [gr.File()],
        "export_subjects_output": [gr.File()],
        "feedback_box": gr.Textbox(label="Feedback", interactive=False)
    }

def create_bulk_prompt_management_tab(style_manager: StyleManager, director_assistant):
        with gr.Accordion("Master Shot List", open=True):
            master_shot_list_df = gr.DataFrame(
                headers=["Scene", "Shot", "Script Reference", "Shot Description", "Shot Size", "People"],
                label="Master Shot List",
                interactive=True
            )
            update_master_shot_list_btn = gr.Button("Update Master Shot List")

        with gr.Accordion("Bulk Director's Notes Generation", open=True):
            visual_style_dropdown = gr.Dropdown(label="Visual Style", choices=style_manager.get_styles())
            director_style_dropdown = gr.Dropdown(label="Director Style", choices=[style['name'] for style in director_assistant.get_director_styles()])
            generate_bulk_notes_btn = gr.Button("Generate Bulk Director's Notes")
            bulk_notes_output = gr.DataFrame(
                headers=["Scene", "Shot", "Script Reference", "Director's Notes", "Shot Description", "Shot Size", "People"],
                label="Generated Director's Notes",
                interactive=True
            )
        
        with gr.Accordion("Bulk Prompt Generation", open=True):
            generate_bulk_prompts_btn = gr.Button("Generate Bulk Prompts")
            bulk_prompts_output = gr.DataFrame(
                headers=["Scene", "Shot", "Concise Prompt", "Medium Prompt", "Detailed Prompt"],
                label="Generated Prompts"
            )

        generate_all_btn = gr.Button("Generate All (Notes + Prompts)")
        export_btn = gr.Button("Export to CSV")
        progress_bar = gr.Progress()
        status_message = gr.Textbox(label="Status", interactive=False)

        return {
            "master_shot_list_df": master_shot_list_df,
            "update_master_shot_list_btn": update_master_shot_list_btn,
            "visual_style_dropdown": visual_style_dropdown,
            "director_style_dropdown": director_style_dropdown,
            "generate_bulk_notes_btn": generate_bulk_notes_btn,
            "bulk_notes_output": bulk_notes_output,
            "generate_bulk_prompts_btn": generate_bulk_prompts_btn,
            "bulk_prompts_output": bulk_prompts_output,
            "generate_all_btn": generate_all_btn,
            "export_btn": export_btn,
            "progress_bar": progress_bar,
            "status_message": status_message,
            "bulk_notes_inputs": [visual_style_dropdown, director_style_dropdown, master_shot_list_df],
            "bulk_notes_outputs": [bulk_notes_output],
            "bulk_prompts_inputs": [bulk_notes_output],
            "bulk_prompts_outputs": [bulk_prompts_output],
        }

def create_project_management_tab(project_manager: ProjectManager):
        with gr.Accordion("💾/📂 Load/Save Project", open=False):
            with gr.Row():
                project_name_input = gr.Textbox(label="Project Name")
                save_project_btn = gr.Button("💾 Save Project")
                load_project_btn = gr.Button("📂 Load Project")
                delete_project_btn = gr.Button("🗑️ Delete Project")
                export_prompts_btn = gr.Button("📤 Export Prompts")

            feedback_box = gr.Textbox(label="Feedback", interactive=False)

            projects_df = gr.DataFrame(
                headers=["Project Name", "Last Modified"],
                label="Saved Projects",
                interactive=False
            )

            prompts_display = gr.TextArea(label="Generated Prompts", lines=10, interactive=False)

        return {
        "project_name_input": project_name_input,
        "save_project_btn": save_project_btn,
        "load_project_btn": load_project_btn,
        "delete_project_btn": delete_project_btn,
        "export_prompts_btn": export_prompts_btn,
        "feedback_box": feedback_box,
        "projects_df": projects_df,
        "prompts_display": prompts_display,
        "save_inputs": [project_name_input],
        "save_outputs": [feedback_box, projects_df],
        "load_inputs": [project_name_input],
        "delete_inputs": [project_name_input],
        "load_outputs": [feedback_box, projects_df, prompts_display],
        "delete_outputs": [feedback_box, projects_df],
    }

def create_music_lab_tab():
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
        
        # Music Lab Interface
        lyrics_textbox = gr.Textbox(label="Lyrics", lines=10)
        audio_upload = gr.File(label="Upload Audio File")
        include_timestamps = gr.Checkbox(label="Include Timestamps")
        transcribe_button = gr.Button("Transcribe")
        
        with gr.Row():
            find_text = gr.Textbox(label="Find")
            replace_text = gr.Textbox(label="Replace")
        replace_button = gr.Button("Replace")
        
        audio_player = gr.Audio(label="Audio Player")

        return {
            "concept_input": concept_input,
            "genre_input": genre_input,
            "descriptors_input": descriptors_input,
            "lyrics_textbox": lyrics_textbox,
            "audio_upload": audio_upload,
            "include_timestamps": include_timestamps,
            "transcribe_button": transcribe_button,
            "find_text": find_text,
            "replace_text": replace_text,
        "replace_button": replace_button,
        "audio_player": audio_player,
    }
def create_master_tabs(style_manager, director_assistant, subject_manager, project_manager):
    with gr.Tabs() as master_tabs:
        with gr.Tab("Script & Director Style"):
            with gr.Accordion("Full Script", open=False):
                full_script_input = gr.Textbox(label="Full Script", lines=10)
            
            with gr.Accordion("Master Shot List", open=True):
                master_shot_list_df = gr.DataFrame(
                    headers=["Timestamp", "Scene", "Shot", "Reference", "Shot Description", "Shot Size", "People", "Places"],
                    label="Master Shot List",
                    interactive=True
                )
            
            with gr.Tabs() as sub_tabs:
                with gr.TabItem("Shot and Prompt Generation"):
                    script_tab_components = create_script_tab(style_manager, director_assistant)
                
                with gr.TabItem("Subject Management"):
                    subject_tab_components = create_subject_management_tab(subject_manager)
                
                with gr.TabItem("Bulk Prompt Management"):
                    bulk_prompt_tab_components = create_bulk_prompt_management_tab(style_manager, director_assistant)
                
                with gr.TabItem("Project Management"):
                    project_tab_components = create_project_management_tab(project_manager)
        
        with gr.Tab("Music Lab"):
            music_lab_tab_components = create_music_lab_tab()
    
    return {
        "master_tabs": master_tabs,
        "full_script_input": full_script_input,
        "master_shot_list_df": master_shot_list_df,
        "script_tab_components": script_tab_components,
        "subject_tab_components": subject_tab_components,
        "bulk_prompt_tab_components": bulk_prompt_tab_components,
        "project_tab_components": project_tab_components,
        "music_lab_tab_components": music_lab_tab_components
    }
