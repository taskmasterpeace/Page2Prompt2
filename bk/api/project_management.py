import asyncio
import os
import json
import pandas as pd
from datetime import datetime
import aiofiles
import logging
from typing import Tuple, List, Dict, Any, Optional
from page2prompt.models.project import Project
from page2prompt.utils.config import config
from page2prompt.utils.helpers import read_json_file, write_json_file

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self):
        self.projects_dir = config.projects_directory

    async def save_project(self, project_name: str, full_script: str, shot_list: pd.DataFrame, subjects: pd.DataFrame, generated_prompts: List[str]) -> Tuple[str, Optional[pd.DataFrame], List[str]]:
        if not project_name:
            logger.error("Attempted to save project with empty name")
            return "Please enter a project name.", None, generated_prompts

        project = Project(
            name=project_name,
            full_script=full_script,
            shot_list=shot_list.to_dict(orient='records'),
            subjects=subjects.to_dict(orient='records'),
            prompts=generated_prompts
        )
        
        file_path = os.path.join(self.projects_dir, f"{project_name}.json")
        try:
            write_json_file(file_path, project.to_dict())
            logger.info(f"Project '{project_name}' saved successfully")
            return f"Project '{project_name}' saved successfully.", await self.list_projects(), generated_prompts
        except IOError as e:
            logger.error(f"Error saving project '{project_name}': {str(e)}")
            return f"Error saving project: {str(e)}", None, generated_prompts

    async def load_project(self, project_name: str) -> Tuple[Optional[str], Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[List[str]], str]:
        file_path = os.path.join(self.projects_dir, f"{project_name}.json")
        try:
            project_data = read_json_file(file_path)
            project = Project.from_dict(project_data)
            
            logger.info(f"Project '{project_name}' loaded successfully")
            return (
                project.full_script,
                pd.DataFrame(project.shot_list),
                pd.DataFrame(project.subjects),
                project.prompts,
                f"Project '{project_name}' loaded successfully."
            )
        except FileNotFoundError:
            logger.error(f"Project '{project_name}' not found")
            return None, None, None, None, f"Project '{project_name}' not found."
        except json.JSONDecodeError:
            logger.error(f"Error reading project file for '{project_name}'. The file may be corrupted.")
            return None, None, None, None, f"Error reading project file for '{project_name}'. The file may be corrupted."
        except Exception as e:
            logger.error(f"Error loading project '{project_name}': {str(e)}")
            return None, None, None, None, f"Error loading project: {str(e)}"

    async def delete_project(self, project_name: str) -> Tuple[str, pd.DataFrame]:
        file_path = os.path.join(self.projects_dir, f"{project_name}.json")
        try:
            os.remove(file_path)
            logger.info(f"Project '{project_name}' deleted successfully")
            return f"Project '{project_name}' deleted successfully.", await self.list_projects()
        except FileNotFoundError:
            logger.error(f"Attempted to delete non-existent project '{project_name}'")
            return f"Project '{project_name}' not found.", await self.list_projects()
        except IOError as e:
            logger.error(f"Error deleting project '{project_name}': {str(e)}")
            return f"Error deleting project: {str(e)}", await self.list_projects()

    async def list_projects(self) -> pd.DataFrame:
        projects = []
        for file in os.listdir(self.projects_dir):
            if file.endswith(".json"):
                file_path = os.path.join(self.projects_dir, file)
                try:
                    project_data = read_json_file(file_path)
                    projects.append({
                        "Project Name": project_data.get("name", "Unknown"),
                        "Last Modified": project_data.get("last_modified", "Unknown")
                    })
                except Exception as e:
                    logger.error(f"Error reading project file {file}: {str(e)}")
        return pd.DataFrame(projects)

    async def export_prompts(self, prompts: List[str], project_name: str) -> str:
        if not project_name:
            logger.error("Attempted to export prompts with empty project name")
            return "Please enter a project name."
        file_path = os.path.join(self.projects_dir, f"{project_name}_prompts.txt")
        try:
            async with aiofiles.open(file_path, "w") as f:
                await f.write("\n\n".join(prompts))
            logger.info(f"Prompts exported to '{file_path}'")
            return f"Prompts exported to '{project_name}_prompts.txt'"
        except IOError as e:
            logger.error(f"Error exporting prompts for project '{project_name}': {str(e)}")
            return f"Error exporting prompts: {str(e)}"
