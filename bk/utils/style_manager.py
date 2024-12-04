from typing import List, Optional
from page2prompt.models.style import Style
from page2prompt.utils.helpers import read_csv_file, write_csv_file

class StyleManager:
    def __init__(self, styles_file: str):
        self.styles_file = styles_file
        self.styles: List[Style] = self._load_styles()

    def _load_styles(self) -> List[Style]:
        try:
            styles_data = read_csv_file(self.styles_file)
            return [Style.from_dict(style) for style in styles_data]
        except FileNotFoundError:
            print(f"Styles file not found: {self.styles_file}")
            return []
        except Exception as e:
            print(f"Error loading styles: {str(e)}")
            return []

    def get_styles(self) -> List[str]:
        return [style.name for style in self.styles]

    def get_style(self, name: str) -> Optional[Style]:
        for style in self.styles:
            if style.name == name:
                return style
        return None

    def add_style(self, style: Style) -> None:
        if not any(s.name == style.name for s in self.styles):
            self.styles.append(style)
            self._save_styles()

    def update_style(self, style: Style) -> None:
        for i, s in enumerate(self.styles):
            if s.name == style.name:
                self.styles[i] = style
                self._save_styles()
                return

    def delete_style(self, name: str) -> None:
        self.styles = [s for s in self.styles if s.name != name]
        self._save_styles()

    def _save_styles(self) -> None:
        styles_data = [style.to_dict() for style in self.styles]
        write_csv_file(self.styles_file, styles_data, fieldnames=["name", "prefix", "suffix", "genre", "descriptors"])
