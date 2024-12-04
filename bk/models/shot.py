from typing import Optional

class Shot:
    def __init__(
        self,
        timestamp: str,
        scene: str,
        shot: str,
        reference: str,
        description: str,
        size: str,
        people: str,
        places: str,
        directors_notes: Optional[str] = None
    ):
        self.timestamp = timestamp
        self.scene = scene
        self.shot = shot
        self.reference = reference
        self.description = description
        self.size = size
        self.people = people
        self.places = places
        self.directors_notes = directors_notes

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "scene": self.scene,
            "shot": self.shot,
            "reference": self.reference,
            "description": self.description,
            "size": self.size,
            "people": self.people,
            "places": self.places,
            "directors_notes": self.directors_notes
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
