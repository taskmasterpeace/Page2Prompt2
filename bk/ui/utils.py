import gradio as gr

def copy_to_clipboard(text):
    return f"Copied to clipboard: {text}"

def send_to_directors_clipboard(text, current_clipboard):
    if current_clipboard:
        return current_clipboard + "\n\n" + text
    return text

def clear_directors_clipboard():
    return ""

def export_directors_clipboard(text):
    return gr.File.update(value=text.encode(), visible=True, filename="directors_clipboard.txt")

def import_directors_clipboard(file):
    if file is not None:
        content = file.decode('utf-8')
        return content
    return ""

def send_all_prompts(concise, normal, detailed, current_clipboard):
    all_prompts = f"Concise:\n{concise}\n\nNormal:\n{normal}\n\nDetailed:\n{detailed}"
    if current_clipboard:
        return current_clipboard + "\n\n" + all_prompts
    return all_prompts

def create_camera_settings(shot, move, size, framing, depth_of_field, camera_type, camera_name, lens_type):
    return {
        k: v for k, v in {
            "shot": shot,
            "move": move,
            "size": size,
            "framing": framing,
            "depth_of_field": depth_of_field,
            "camera_type": camera_type,
            "camera_name": camera_name,
            "lens_type": lens_type
        }.items() if v != "AI Suggest"
    }
import gradio as gr

def copy_to_clipboard(text):
    return f"Copied to clipboard: {text}"

def send_to_directors_clipboard(text, current_clipboard):
    if current_clipboard:
        return current_clipboard + "\n\n" + text
    return text

def clear_directors_clipboard():
    return ""

def export_directors_clipboard(text):
    return gr.File.update(value=text.encode(), visible=True, filename="directors_clipboard.txt")

def import_directors_clipboard(file):
    if file is not None:
        content = file.decode('utf-8')
        return content
    return ""

def send_all_prompts(concise, normal, detailed, current_clipboard):
    all_prompts = f"Concise:\n{concise}\n\nNormal:\n{normal}\n\nDetailed:\n{detailed}"
    if current_clipboard:
        return current_clipboard + "\n\n" + all_prompts
    return all_prompts

def create_camera_settings(shot, move, size, framing, depth_of_field, camera_type, camera_name, lens_type):
    return {
        k: v for k, v in {
            "shot": shot,
            "move": move,
            "size": size,
            "framing": framing,
            "depth_of_field": depth_of_field,
            "camera_type": camera_type,
            "camera_name": camera_name,
            "lens_type": lens_type
        }.items() if v != "AI Suggest"
    }
