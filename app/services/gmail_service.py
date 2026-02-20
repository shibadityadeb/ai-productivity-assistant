import os
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from pathlib import Path
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailService:
    """Service for interacting with Gmail API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.creds: Optional[Credentials] = None
        self.service = None
        
    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        try:
            creds_path = Path(self.settings.gmail_credentials_path)
            
            # Load existing credentials
            if creds_path.exists():
                with open(creds_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # This would need OAuth flow setup
                    logger.warning("No valid credentials found. OAuth flow needed.")
                    return False
                
                # Save credentials
                creds_path.parent.mkdir(parents=True, exist_ok=True)
                with open(creds_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            return False
    
    async def list_messages(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """List recent email messages."""
        if not self.service:
            self.authenticate()
        
        try:
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Retrieved {len(messages)} messages")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to list messages: {str(e)}")
            raise
    
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get a specific email message."""
        if not self.service:
            self.authenticate()
        
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id
            ).execute()
            
            logger.info(f"Retrieved message {message_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to get message: {str(e)}")
            raise
    
    async def send_message(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email message."""
        if not self.service:
            self.authenticate()
        
        try:
            from email.mime.text import MIMEText
            import base64
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            logger.info(f"Sent message to {to}")
            return sent_message
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
