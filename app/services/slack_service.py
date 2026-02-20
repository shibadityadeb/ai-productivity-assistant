from typing import List, Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SlackService:
    """Service for interacting with Slack API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[WebClient] = None
        
        if self.settings.slack_bot_token:
            self.client = WebClient(token=self.settings.slack_bot_token)
    
    async def list_channels(self) -> List[Dict[str, Any]]:
        """List all channels in workspace."""
        if not self.client:
            raise ValueError("Slack client not initialized")
        
        try:
            response = self.client.conversations_list()
            channels = response.get('channels', [])
            logger.info(f"Retrieved {len(channels)} channels")
            return channels
            
        except SlackApiError as e:
            logger.error(f"Failed to list channels: {e.response['error']}")
            raise
    
    async def send_message(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a message to a Slack channel."""
        if not self.client:
            raise ValueError("Slack client not initialized")
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            logger.info(f"Message sent to channel {channel}")
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Failed to send message: {e.response['error']}")
            raise
    
    async def get_channel_history(self, channel: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from a channel."""
        if not self.client:
            raise ValueError("Slack client not initialized")
        
        try:
            response = self.client.conversations_history(
                channel=channel,
                limit=limit
            )
            messages = response.get('messages', [])
            logger.info(f"Retrieved {len(messages)} messages from {channel}")
            return messages
            
        except SlackApiError as e:
            logger.error(f"Failed to get channel history: {e.response['error']}")
            raise
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a Slack user."""
        if not self.client:
            raise ValueError("Slack client not initialized")
        
        try:
            response = self.client.users_info(user=user_id)
            user = response.get('user', {})
            logger.info(f"Retrieved info for user {user_id}")
            return user
            
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e.response['error']}")
            raise
    
    async def update_status(self, status_text: str, status_emoji: str = ":robot_face:") -> Dict[str, Any]:
        """Update the bot's status."""
        if not self.client:
            raise ValueError("Slack client not initialized")
        
        try:
            response = self.client.users_profile_set(
                profile={
                    "status_text": status_text,
                    "status_emoji": status_emoji
                }
            )
            logger.info(f"Status updated to: {status_text}")
            return response.data
            
        except SlackApiError as e:
            logger.error(f"Failed to update status: {e.response['error']}")
            raise
