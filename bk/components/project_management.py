from typing import Dict, Any, List
from datetime import datetime

class ProjectManager:
    def __init__(self):
        self.projects = {}

    def save_project(self, name: str, data: Dict[str, Any]) -> None:
        self.projects[name] = {
            "data": data,
            "last_modified": datetime.now()
        }

    def load_project(self, name: str) -> Dict[str, Any]:
        return self.projects.get(name, {}).get("data", {})

    def delete_project(self, name: str) -> None:
        if name in self.projects:
            del self.projects[name]

    def get_project_list(self) -> List[Dict[str, Any]]:
        return [
            {"name": name, "last_modified": project["last_modified"]}
            for name, project in self.projects.items()
        ]
