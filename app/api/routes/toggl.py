from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.toggl_service import TogglService
from app.models.schemas import TimeEntryCreate, TimeEntryQuery
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/toggl", tags=["Toggl"])


def get_toggl_service() -> TogglService:
    """Dependency for Toggl service."""
    return TogglService()


@router.get("/current")
async def get_current_entry(
    service: TogglService = Depends(get_toggl_service)
) -> Dict[str, Any]:
    """Get currently running time entry."""
    try:
        entry = await service.get_current_time_entry()
        return {
            "status": "success",
            "entry": entry
        }
    except Exception as e:
        logger.error(f"Failed to get current entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def get_time_entries(
    query: TimeEntryQuery = Depends(),
    service: TogglService = Depends(get_toggl_service)
) -> Dict[str, Any]:
    """Get time entries for a date range."""
    try:
        entries = await service.get_time_entries(
            start_date=query.start_date,
            end_date=query.end_date
        )
        return {
            "status": "success",
            "count": len(entries),
            "entries": entries
        }
    except Exception as e:
        logger.error(f"Failed to get time entries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_time_entry(
    entry: TimeEntryCreate,
    service: TogglService = Depends(get_toggl_service)
) -> Dict[str, Any]:
    """Start a new time entry."""
    try:
        result = await service.start_time_entry(
            description=entry.description,
            project_id=entry.project_id,
            tags=entry.tags
        )
        return {
            "status": "success",
            "message": "Time entry started",
            "entry": result
        }
    except Exception as e:
        logger.error(f"Failed to start time entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{entry_id}")
async def stop_time_entry(
    entry_id: int,
    service: TogglService = Depends(get_toggl_service)
) -> Dict[str, Any]:
    """Stop a running time entry."""
    try:
        result = await service.stop_time_entry(entry_id)
        return {
            "status": "success",
            "message": "Time entry stopped",
            "entry": result
        }
    except Exception as e:
        logger.error(f"Failed to stop time entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def get_projects(
    service: TogglService = Depends(get_toggl_service)
) -> Dict[str, Any]:
    """Get all projects in workspace."""
    try:
        projects = await service.get_projects()
        return {
            "status": "success",
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        logger.error(f"Failed to get projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
