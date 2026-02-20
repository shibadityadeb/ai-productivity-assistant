import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integrations.gmail import GmailClient, GmailAPIError, AuthenticationError
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GmailService:
    """Enhanced Gmail service using the production-ready Gmail integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = GmailClient(
            credentials_file='credentials/gmail_credentials.json',
            token_file='credentials/gmail_token.pickle'
        )
        self._authenticated = False
    
    def _ensure_authenticated(self):
        """Ensure the client is authenticated."""
        if not self._authenticated:
            try:
                self.client.authenticate()
                self._authenticated = True
                logger.info("Gmail service authenticated successfully")
            except AuthenticationError as e:
                logger.error(f"Gmail authentication failed: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected authentication error: {str(e)}")
                raise
    
    async def list_messages(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """List email messages with optional query."""
        self._ensure_authenticated()
        
        try:
            if query:
                messages = self.client.search_emails(query, max_results)
            else:
                messages = self.client.get_unread_emails(max_results)
            
            logger.info(f"Retrieved {len(messages)} messages")
            return messages
            
        except GmailAPIError as e:
            logger.error(f"Failed to list messages: {str(e)}")
            raise
    
    async def get_important_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get important emails."""
        self._ensure_authenticated()
        
        try:
            messages = self.client.get_important_emails(max_results)
            logger.info(f"Retrieved {len(messages)} important emails")
            return messages
        except GmailAPIError as e:
            logger.error(f"Failed to get important emails: {str(e)}")
            raise
    
    async def get_starred_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get starred emails."""
        self._ensure_authenticated()
        
        try:
            messages = self.client.get_starred_emails(max_results)
            logger.info(f"Retrieved {len(messages)} starred emails")
            return messages
        except GmailAPIError as e:
            logger.error(f"Failed to get starred emails: {str(e)}")
            raise
    
    async def get_unread_emails(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Get unread emails."""
        self._ensure_authenticated()
        
        try:
            messages = self.client.get_unread_emails(max_results)
            logger.info(f"Retrieved {len(messages)} unread emails")
            return messages
        except GmailAPIError as e:
            logger.error(f"Failed to get unread emails: {str(e)}")
            raise
    
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get a specific email message by ID."""
        self._ensure_authenticated()
        
        try:
            message = self.client._get_message_details(message_id)
            if not message:
                raise GmailAPIError(f"Message {message_id} not found")
            
            logger.info(f"Retrieved message {message_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to get message: {str(e)}")
            raise
    
    async def send_message(
        self, 
        to: str, 
        subject: str, 
        body: str,
        cc: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send an email message."""
        self._ensure_authenticated()
        
        try:
            result = self.client.send_email(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                attachments=attachments
            )
            
            logger.info(f"Sent message to {to}")
            return result
            
        except GmailAPIError as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get Gmail profile information."""
        self._ensure_authenticated()
        
        try:
            profile = self.client.get_profile()
            logger.info(f"Retrieved profile for {profile.get('emailAddress')}")
            return profile
        except GmailAPIError as e:
            logger.error(f"Failed to get profile: {str(e)}")
            raise
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        self._ensure_authenticated()
        
        try:
            return self.client.mark_as_read(message_id)
        except GmailAPIError as e:
            logger.error(f"Failed to mark as read: {str(e)}")
            raise
    
    async def mark_as_starred(self, message_id: str) -> bool:
        """Star an email."""
        self._ensure_authenticated()
        
        try:
            return self.client.mark_as_starred(message_id)
        except GmailAPIError as e:
            logger.error(f"Failed to mark as starred: {str(e)}")
            raise
    
    async def search_emails(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search emails with Gmail query syntax."""
        self._ensure_authenticated()
        
        try:
            messages = self.client.search_emails(query, max_results)
            logger.info(f"Search '{query}' found {len(messages)} messages")
            return messages
        except GmailAPIError as e:
            logger.error(f"Search failed: {str(e)}")
            raise