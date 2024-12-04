import gradio as gr
from page2prompt.api.audio_processing import AudioProcessor

def create_music_lab_interface():
    audio_processor = AudioProcessor()

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
        
        def transcribe_audio_wrapper(audio_file, include_timestamps):
            return audio_processor.transcribe_audio(audio_file, include_timestamps)
        
        transcribe_button.click(
            transcribe_audio_wrapper,
            inputs=[audio_upload, include_timestamps],
            outputs=lyrics_textbox
        )
        
        with gr.Row():
            find_text = gr.Textbox(label="Find", scale=2)
            replace_text = gr.Textbox(label="Replace", scale=2)
            replace_button = gr.Button("Replace")
        
        def search_and_replace_lyrics_wrapper(lyrics, find, replace):
            return audio_processor.search_and_replace_lyrics(lyrics, find, replace)
        
        replace_button.click(
            search_and_replace_lyrics_wrapper,
            inputs=[lyrics_textbox, find_text, replace_text],
            outputs=lyrics_textbox
        )

    with gr.Accordion("Music Player 🎧", open=True):
        audio_player = gr.Audio(label="Play Uploaded MP3", type="filepath")
    
        def update_audio_player(file):
            if file is not None:
                return file.name
            return None
    
        audio_upload.change(
            update_audio_player,
            inputs=[audio_upload],
            outputs=[audio_player]
        )

    return lyrics_textbox, audio_upload, include_timestamps, transcribe_button, find_text, replace_text, replace_button, audio_player
