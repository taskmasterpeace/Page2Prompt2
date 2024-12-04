from typing import List, Dict, Any
from datetime import datetime

class Project:
    def __init__(
        self,
        name: str,
        full_script: str,
        shot_list: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        prompts: List[str],
        last_modified: datetime = None
    ):
        self.name = name
        self.full_script = full_script
        self.shot_list = shot_list
        self.subjects = subjects
        self.prompts = prompts
        self.last_modified = last_modified or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "full_script": self.full_script,
            "shot_list": self.shot_list,
            "subjects": self.subjects,
            "prompts": self.prompts,
            "last_modified": self.last_modified.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(
            name=data["name"],
            full_script=data["full_script"],
            shot_list=data["shot_list"],
            subjects=data["subjects"],
            prompts=data["prompts"],
            last_modified=datetime.fromisoformat(data["last_modified"])
        )
