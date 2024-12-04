import csv
import os
import random
import logging
from typing import Dict, List, Tuple, Optional
from page2prompt.models.style import Style
from page2prompt.utils.helpers import read_csv_file, write_csv_file

logger = logging.getLogger(__name__)

class StyleManager:
    def __init__(self, styles_file: str):
        self.styles_file = styles_file
        self.styles = self._load_styles()

    def _load_styles(self) -> List[Style]:
        try:
            styles_data = read_csv_file(self.styles_file)
            return [Style(name=style['name'], prefix=style['prefix'], suffix=style['suffix']) for style in styles_data]
        except Exception as e:
            logger.error(f"Error loading styles: {str(e)}")
            return []

    def get_styles(self) -> List[str]:
        return [style.name for style in self.styles]

    def get_style(self, name: str) -> Optional[Style]:
        for style in self.styles:
            if style.name == name:
                return style
        logger.warning(f"Style '{name}' not found")
        return None

    def get_style_details(self, name: str) -> Optional[Dict[str, str]]:
        style = self.get_style(name)
        if style:
            return {'prefix': style.prefix, 'suffix': style.suffix}
        return None

    def add_style(self, style: Style) -> None:
        if not any(s.name == style.name for s in self.styles):
            self.styles.append(style)
            self._save_styles()
            logger.info(f"Style '{style.name}' added successfully")
        else:
            logger.warning(f"Style '{style.name}' already exists")

    def update_style(self, style: Style) -> None:
        for i, s in enumerate(self.styles):
            if s.name == style.name:
                self.styles[i] = style
                self._save_styles()
                logger.info(f"Style '{style.name}' updated successfully")
                return
        logger.warning(f"Style '{style.name}' not found for update")

    def delete_style(self, name: str) -> None:
        self.styles = [s for s in self.styles if s.name != name]
        self._save_styles()
        logger.info(f"Style '{name}' deleted successfully")

    def _save_styles(self) -> None:
        try:
            styles_data = [style.to_dict() for style in self.styles]
            write_csv_file(self.styles_file, styles_data, fieldnames=["name", "prefix", "suffix", "genre", "descriptors"])
            logger.info("Styles saved successfully")
        except Exception as e:
            logger.error(f"Error saving styles: {str(e)}")

    @staticmethod
    def create_random_style() -> Style:
        adjectives = ["Vibrant", "Moody", "Retro", "Futuristic", "Ethereal", "Gritty", "Surreal", "Minimalist"]
        nouns = ["Watercolor", "Neon", "Cyberpunk", "Impressionist", "Abstract", "Pop Art", "Noir", "Steampunk"]
    
        style_name = f"{random.choice(adjectives)} {random.choice(nouns)}"
    
        prefix_templates = ["A {style} image of", "In the style of {style}:", "Reimagined as {style}:"]
        prefix = random.choice(prefix_templates).format(style=style_name)
    
        characteristics = ["high contrast", "soft focus", "vivid colors", "dramatic lighting", "muted tones", "sharp details", "dreamy atmosphere", "bold outlines"]
        suffix = "; ".join(random.sample(characteristics, random.randint(2, 4)))
    
        genres = ["Fantasy", "Sci-Fi", "Romance", "Horror", "Documentary", "Action", "Drama", "Comedy"]
        genre = random.choice(genres)
    
        descriptor_categories = {
            "Color": ["saturated", "monochromatic", "pastel", "neon", "earthy"],
            "Texture": ["smooth", "grainy", "glossy", "rough", "metallic"],
            "Mood": ["serene", "intense", "whimsical", "melancholic", "energetic"],
            "Technique": ["brush strokes", "digital art", "photorealistic", "collage", "vector graphics"]
        }
    
        descriptors = [random.choice(category) for category in descriptor_categories.values()]
        descriptors_str = "; ".join(descriptors)
    
        return Style(
            name=style_name,
            prefix=prefix,
            suffix=suffix,
            genre=genre,
            descriptors=descriptors_str
        )

    def generate_random_style(self) -> Tuple[str, str]:
        try:
            new_style = self.create_random_style()
            self.add_style(new_style)
            logger.info(f"Generated new style: {new_style.name}")
            return f"Generated new style: {new_style.name}", new_style.name
        except Exception as e:
            logger.error(f"Error generating random style: {str(e)}")
            return "Error generating random style", ""
