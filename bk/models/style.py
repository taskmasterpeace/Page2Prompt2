from typing import Optional

class Style:
    def __init__(
        self,
        name: str,
        prefix: str,
        suffix: str,
        genre: Optional[str] = None,
        descriptors: Optional[str] = None
    ):
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.genre = genre
        self.descriptors = descriptors

    def to_dict(self) -> dict:
        return {
            "Style Name": self.name,
            "Prefix": self.prefix,
            "Suffix": self.suffix,
            "Genre": self.genre,
            "Descriptors": self.descriptors
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Style':
        return cls(
            name=data["Style Name"],
            prefix=data["Prefix"],
            suffix=data["Suffix"],
            genre=data.get("Genre"),
            descriptors=data.get("Descriptors")
        )
class Style:
    def __init__(
        self,
        name: str,
        prefix: str,
        suffix: str,
        genre: str = None,
        descriptors: str = None
    ):
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.genre = genre
        self.descriptors = descriptors

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "genre": self.genre,
            "descriptors": self.descriptors
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Style':
        return cls(
            name=data["name"],
            prefix=data["prefix"],
            suffix=data["suffix"],
            genre=data.get("genre"),
            descriptors=data.get("descriptors")
        )
