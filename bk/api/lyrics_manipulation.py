import re

class LyricsManipulator:
    @staticmethod
    def search_and_replace_lyrics(lyrics: str, search_term: str, replace_term: str) -> str:
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        return pattern.sub(replace_term, lyrics)
