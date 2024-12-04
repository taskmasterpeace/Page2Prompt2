from openai import OpenAI
import os

class AudioTranscriber:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def transcribe_audio(self, audio_file, include_timestamps=False):
        if audio_file is None:
            return "Please upload an MP3 file."

        try:
            with open(audio_file.name, "rb") as file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    response_format='srt' if include_timestamps else 'text'
                )

            if include_timestamps:
                formatted_transcript = ""
                for line in response.strip().split('\n\n'):
                    parts = line.split('\n')
                    if len(parts) >= 3:
                        time_range, text = parts[1], parts[2]
                        formatted_transcript += f"{time_range} {text}\n"
                return formatted_transcript if formatted_transcript else "Error: Unable to parse SRT format."
            else:
                return response
        except Exception as e:
            return f"Error during transcription: {str(e)}"
