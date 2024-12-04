from page2prompt.api.audio_transcription import AudioTranscriber
from page2prompt.api.lyrics_manipulation import LyricsManipulator

class AudioProcessor:
    def __init__(self):
        self.audio_transcriber = AudioTranscriber()
        self.lyrics_manipulator = LyricsManipulator()

    def transcribe_audio(self, audio_file, include_timestamps):
        return self.audio_transcriber.transcribe_audio(audio_file, include_timestamps)

    def search_and_replace_lyrics(self, lyrics, find, replace):
        return self.lyrics_manipulator.search_and_replace_lyrics(lyrics, find, replace)
