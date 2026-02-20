from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.slack_service import SlackService
from app.models.schemas import SlackMessage, SlackChannelHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/slack", tags=["Slack"])


def get_slack_service() -> SlackService:
    """Dependency for Slack service."""
    return SlackService()


@router.get("/channels")
async def list_channels(
    service: SlackService = Depends(get_slack_service)
) -> Dict[str, Any]:
    """List all Slack channels."""
    try:
        channels = await service.list_channels()
        return {
            "status": "success",
            "count": len(channels),
            "channels": channels
        }
    except Exception as e:
        logger.error(f"Failed to list channels: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages")
async def send_message(
    message: SlackMessage,
    service: SlackService = Depends(get_slack_service)
) -> Dict[str, Any]:
    """Send a message to a Slack channel."""
    try:
        result = await service.send_message(
            channel=message.channel,
            text=message.text,
            blocks=message.blocks
        )
        return {
            "status": "success",
            "message": "Message sent successfully",
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/{channel_id}/history")
async def get_channel_history(
    channel_id: str,
    limit: int = 10,
    service: SlackService = Depends(get_slack_service)
) -> Dict[str, Any]:
    """Get message history from a Slack channel."""
    try:
        messages = await service.get_channel_history(channel_id, limit)
        return {
            "status": "success",
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Failed to get channel history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_info(
    user_id: str,
    service: SlackService = Depends(get_slack_service)
) -> Dict[str, Any]:
    """Get information about a Slack user."""
    try:
        user = await service.get_user_info(user_id)
        return {
            "status": "success",
            "user": user
        }
    except Exception as e:
        logger.error(f"Failed to get user info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/status")
async def update_status(
    status_text: str,
    status_emoji: str = ":robot_face:",
    service: SlackService = Depends(get_slack_service)
) -> Dict[str, Any]:
    """Update the bot's Slack status."""
    try:
        result = await service.update_status(status_text, status_emoji)
        return {
            "status": "success",
            "message": "Status updated successfully",
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to update status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
