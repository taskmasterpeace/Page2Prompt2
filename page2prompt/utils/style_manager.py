import csv
import os
from typing import Dict, List, Tuple
from langchain.prompts import PromptTemplate

class StyleManager:
    def __init__(self, styles_file: str):
        self.styles_file = styles_file
        self.styles = self._load_styles()

    def _load_styles(self) -> List[Dict]:
        """Loads styles from the CSV file."""
        styles = []
        try:
            with open(self.styles_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                if not fieldnames or "Style Name" not in fieldnames:
                    print(f"Error: 'Style Name' column not found in {self.styles_file}")
                    print(f"Available columns: {', '.join(fieldnames) if fieldnames else 'None'}")
                    return []
                for row in reader:
                    styles.append(row)
            if not styles:
                print(f"Warning: No styles found in {self.styles_file}")
        except FileNotFoundError:
            print(f"Error: Styles file not found at {self.styles_file}")
        except csv.Error as e:
            print(f"Error reading CSV file: {e}")
        return styles

    def get_styles(self) -> List[str]:
        """Returns the list of style names."""
        return [style.get("Style Name", "") for style in self.styles if "Style Name" in style]

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

    def get_full_style_description(self, style_name: str) -> str:
        """Returns the full style description for the given style name."""
        style = self.get_style(style_name)
        if not style:
            return ""
        return f"{style.get('Prefix', '')} {style.get('Suffix', '')}".strip()

    def get_style_prefix_suffix(self, style_name: str) -> Tuple[str, str]:
        """Returns the prefix and suffix for the given style name."""
        style = self.get_style(style_name)
        return style.get("Prefix", ""), style.get("Suffix", "")

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

    def print_styles(self):
        """Prints the contents of the styles for debugging."""
        print(f"Styles loaded from {self.styles_file}:")
        for style in self.styles:
            print(style)
