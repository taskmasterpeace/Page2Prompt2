import csv
from typing import Dict, List
from langchain.prompts import PromptTemplate

class StyleManager:
    def __init__(self, styles_file: str = "styles.csv"):
        self.styles_file = styles_file
        self.styles = self._load_styles()

    def _load_styles(self) -> List[Dict]:
        """Loads styles from the CSV file."""
        styles = []
        try:
            with open(self.styles_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    styles.append(row)
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(self.styles_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["Style Name", "Prefix", "Suffix", "Genre", "Descriptors"])
                writer.writeheader()
        return styles

    def get_styles(self) -> List[str]:
        """Returns the list of style names."""
        return [style["Style Name"] for style in self.styles]

    def get_style(self, style_name: str) -> Dict:
        """Returns the style with the given name."""
        for style in self.styles:
            if style["Style Name"] == style_name:
                return style
        return {}  # Return an empty dictionary if the style is not found

    def get_style_prefix(self, style_name: str) -> str:
        """Returns the prefix for the given style name."""
        style = self.get_style(style_name)
        return style.get("Prefix", "")

    def get_style_suffix(self, style_name: str) -> str:
        """Returns the suffix for the given style name."""
        style = self.get_style(style_name)
        return style.get("Suffix", "")

    def get_style_prefix(self, style_name: str) -> str:
        """Returns the prefix for the given style name."""
        style = self.get_style(style_name)
        return style.get("Prefix", "")

    def get_style_suffix(self, style_name: str) -> str:
        """Returns the suffix for the given style name."""
        style = self.get_style(style_name)
        return style.get("Suffix", "")

    def add_style(self, style_data: Dict) -> None:
        """Adds a new style to the list and saves to the CSV file."""
        self.styles.append(style_data)
        self._save_styles()

    def update_style(self, style_data: Dict) -> None:
        """Updates an existing style in the list and saves to the CSV file."""
        for i, style in enumerate(self.styles):
            if style["Style Name"] == style_data["Style Name"]:
                self.styles[i] = style_data
                break
        self._save_styles()

    def delete_style(self, style_name: str) -> None:
        """Deletes a style from the list and saves to the CSV file."""
        self.styles = [s for s in self.styles if s["Style Name"] != style_name]
        self._save_styles()

    def _save_styles(self) -> None:
        """Saves the styles to the CSV file."""
        with open(self.styles_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Style Name", "Prefix", "Suffix", "Genre", "Descriptors"])
            writer.writeheader()
            writer.writerows(self.styles)
