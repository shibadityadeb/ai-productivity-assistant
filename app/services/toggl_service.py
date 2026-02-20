from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TogglService:
    """Service for interacting with Toggl Track API."""
    
    BASE_URL = "https://api.track.toggl.com/api/v9"
    
    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Content-Type": "application/json"
        }
        self.auth = (self.settings.toggl_api_token, "api_token")
    
    async def get_current_time_entry(self) -> Optional[Dict[str, Any]]:
        """Get currently running time entry."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/me/time_entries/current",
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Current time entry: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get current time entry: {str(e)}")
            raise
    
    async def get_time_entries(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get time entries for a date range."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = requests.get(
                f"{self.BASE_URL}/me/time_entries",
                headers=self.headers,
                auth=self.auth,
                params=params
            )
            response.raise_for_status()
            
            entries = response.json()
            logger.info(f"Retrieved {len(entries)} time entries")
            return entries
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get time entries: {str(e)}")
            raise
    
    async def start_time_entry(self, description: str, project_id: Optional[int] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Start a new time entry."""
        try:
            workspace_id = int(self.settings.toggl_workspace_id)
            
            payload = {
                "description": description,
                "workspace_id": workspace_id,
                "created_with": "AI Productivity Assistant"
            }
            
            if project_id:
                payload["project_id"] = project_id
            if tags:
                payload["tags"] = tags
            
            response = requests.post(
                f"{self.BASE_URL}/workspaces/{workspace_id}/time_entries",
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            response.raise_for_status()
            
            entry = response.json()
            logger.info(f"Started time entry: {description}")
            return entry
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start time entry: {str(e)}")
            raise
    
    async def stop_time_entry(self, entry_id: int) -> Dict[str, Any]:
        """Stop a running time entry."""
        try:
            workspace_id = int(self.settings.toggl_workspace_id)
            
            response = requests.patch(
                f"{self.BASE_URL}/workspaces/{workspace_id}/time_entries/{entry_id}/stop",
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            
            entry = response.json()
            logger.info(f"Stopped time entry: {entry_id}")
            return entry
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to stop time entry: {str(e)}")
            raise
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects in workspace."""
        try:
            workspace_id = int(self.settings.toggl_workspace_id)
            
            response = requests.get(
                f"{self.BASE_URL}/workspaces/{workspace_id}/projects",
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            
            projects = response.json()
            logger.info(f"Retrieved {len(projects)} projects")
            return projects
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get projects: {str(e)}")
            raise
