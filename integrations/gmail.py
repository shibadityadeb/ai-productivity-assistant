"""
Production-Ready Gmail API Integration with OAuth2 Authentication

This module provides a robust Gmail API client with:
- OAuth2 authentication and token management
- Automatic token refresh
- Read important/starred emails
- Comprehensive error handling
- Rate limiting protection
- Retry logic
"""

import os
import pickle
import base64
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import structlog

logger = structlog.get_logger(__name__)

# Gmail API scopes - adjust based on your needs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]


class GmailAPIError(Exception):
    """Base exception for Gmail API errors."""
    pass


class AuthenticationError(GmailAPIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(GmailAPIError):
    """Raised when rate limit is exceeded."""
    pass


class GmailClient:
    """
    Production-ready Gmail API client with OAuth2 authentication.
    
    Features:
    - Automatic token refresh
    - Rate limiting protection
    - Retry logic with exponential backoff
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        credentials_file: str = 'credentials/gmail_credentials.json',
        token_file: str = 'credentials/gmail_token.pickle',
        max_retries: int = 3
    ):
        """
        Initialize Gmail client.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load access token
            max_retries: Maximum number of retries for API calls
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.max_retries = max_retries
        self.creds: Optional[Credentials] = None
        self.service = None
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        logger.info("Gmail client initialized", 
                   credentials_file=str(self.credentials_file),
                   token_file=str(self.token_file))
    
    def authenticate(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Args:
            force_reauth: Force re-authentication even if token exists
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Load existing token
            if self.token_file.exists() and not force_reauth:
                logger.info("Loading existing token", token_file=str(self.token_file))
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Refresh token if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    logger.info("Refreshing expired token")
                    self.creds.refresh(Request())
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error("Token refresh failed", error=str(e))
                    self.creds = None
            
            # Get new credentials if needed
            if not self.creds or not self.creds.valid:
                if not self.credentials_file.exists():
                    raise AuthenticationError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                
                logger.info("Starting OAuth2 flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), 
                    SCOPES,
                    redirect_uri='http://localhost:8080/'
                )
                
                # Run local server for OAuth callback
                self.creds = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    success_message='Authentication successful! You can close this window.'
                )
                logger.info("OAuth2 flow completed successfully")
            
            # Save credentials
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            logger.info("Token saved", token_file=str(self.token_file))
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail service initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            raise AuthenticationError(f"Failed to authenticate: {str(e)}")
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _retry_request(self, request_func, *args, **kwargs) -> Any:
        """
        Retry API request with exponential backoff.
        
        Args:
            request_func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            API response
            
        Raises:
            GmailAPIError: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                return request_func(*args, **kwargs)
                
            except HttpError as e:
                if e.resp.status == 429:  # Rate limit
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.warning(
                        "Rate limit hit, retrying",
                        attempt=attempt + 1,
                        wait_time=wait_time
                    )
                    time.sleep(wait_time)
                    
                    if attempt == self.max_retries - 1:
                        raise RateLimitError("Rate limit exceeded after retries")
                    continue
                    
                elif e.resp.status in [401, 403]:  # Auth errors
                    logger.error("Authentication error", status=e.resp.status)
                    raise AuthenticationError(f"Auth error: {str(e)}")
                    
                elif e.resp.status >= 500:  # Server errors
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(
                            "Server error, retrying",
                            attempt=attempt + 1,
                            wait_time=wait_time,
                            status=e.resp.status
                        )
                        time.sleep(wait_time)
                        continue
                    raise GmailAPIError(f"Server error: {str(e)}")
                    
                else:
                    raise GmailAPIError(f"API error: {str(e)}")
                    
            except Exception as e:
                logger.error("Unexpected error", error=str(e))
                raise GmailAPIError(f"Unexpected error: {str(e)}")
        
        raise GmailAPIError("Max retries exceeded")
    
    def get_important_emails(
        self,
        max_results: int = 10,
        include_spam_trash: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch important emails.
        
        Args:
            max_results: Maximum number of emails to fetch
            include_spam_trash: Include emails from spam/trash
            
        Returns:
            List of email dictionaries with subject, sender, snippet, etc.
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info("Fetching important emails", max_results=max_results)
            
            # Build query for important emails
            query = 'is:important'
            if not include_spam_trash:
                query += ' -in:spam -in:trash'
            
            # List messages
            results = self._retry_request(
                self.service.users().messages().list,
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info("Found important emails", count=len(messages))
            
            # Fetch details for each message
            emails = []
            for message in messages:
                email_data = self._get_message_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info("Fetched email details", count=len(emails))
            return emails
            
        except Exception as e:
            logger.error("Failed to fetch important emails", error=str(e))
            raise
    
    def get_starred_emails(
        self,
        max_results: int = 10,
        include_spam_trash: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch starred emails.
        
        Args:
            max_results: Maximum number of emails to fetch
            include_spam_trash: Include emails from spam/trash
            
        Returns:
            List of email dictionaries with subject, sender, snippet, etc.
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info("Fetching starred emails", max_results=max_results)
            
            # Build query for starred emails
            query = 'is:starred'
            if not include_spam_trash:
                query += ' -in:spam -in:trash'
            
            # List messages
            results = self._retry_request(
                self.service.users().messages().list,
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info("Found starred emails", count=len(messages))
            
            # Fetch details for each message
            emails = []
            for message in messages:
                email_data = self._get_message_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info("Fetched email details", count=len(emails))
            return emails
            
        except Exception as e:
            logger.error("Failed to fetch starred emails", error=str(e))
            raise
    
    def get_unread_emails(
        self,
        max_results: int = 20,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch unread emails with optional additional query.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Additional Gmail search query (e.g., 'from:someone@example.com')
            
        Returns:
            List of email dictionaries
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            search_query = 'is:unread -in:spam -in:trash'
            if query:
                search_query += f' {query}'
            
            logger.info("Fetching unread emails", max_results=max_results, query=search_query)
            
            results = self._retry_request(
                self.service.users().messages().list,
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info("Found unread emails", count=len(messages))
            
            emails = []
            for message in messages:
                email_data = self._get_message_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error("Failed to fetch unread emails", error=str(e))
            raise
    
    def _get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with email details or None if error
        """
        try:
            message = self._retry_request(
                self.service.users().messages().get,
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract body/snippet
            snippet = message.get('snippet', '')
            body = self._extract_body(message['payload'])
            
            # Parse date
            date_str = header_dict.get('date', '')
            date_parsed = self._parse_date(date_str)
            
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': header_dict.get('subject', '(No Subject)'),
                'from': header_dict.get('from', 'Unknown'),
                'to': header_dict.get('to', ''),
                'cc': header_dict.get('cc', ''),
                'date': date_str,
                'date_parsed': date_parsed,
                'snippet': snippet,
                'body': body,
                'labels': message.get('labelIds', []),
                'is_unread': 'UNREAD' in message.get('labelIds', []),
                'is_starred': 'STARRED' in message.get('labelIds', []),
                'is_important': 'IMPORTANT' in message.get('labelIds', []),
            }
            
            return email_data
            
        except Exception as e:
            logger.error("Failed to get message details", message_id=message_id, error=str(e))
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from message payload.
        
        Args:
            payload: Message payload
            
        Returns:
            Email body text
        """
        try:
            if 'body' in payload and 'data' in payload['body']:
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif 'parts' in part:
                        # Recursive for nested parts
                        body = self._extract_body(part)
                        if body:
                            return body
            
            return ''
            
        except Exception as e:
            logger.warning("Failed to extract body", error=str(e))
            return ''
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime object."""
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception as e:
            logger.warning("Failed to parse date", date=date_str, error=str(e))
            return None
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send an email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (comma-separated)
            bcc: BCC recipients (comma-separated)
            attachments: List of file paths to attach
            
        Returns:
            Sent message metadata
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info("Sending email", to=to, subject=subject)
            
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._attach_file(message, file_path)
            
            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send
            result = self._retry_request(
                self.service.users().messages().send,
                userId='me',
                body={'raw': raw}
            ).execute()
            
            logger.info("Email sent successfully", message_id=result['id'])
            return result
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            raise
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach file to email message."""
        try:
            file_path = Path(file_path)
            
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={file_path.name}'
            )
            
            message.attach(part)
            logger.debug("Attached file", filename=file_path.name)
            
        except Exception as e:
            logger.error("Failed to attach file", file_path=file_path, error=str(e))
            raise
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if successful
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            self._retry_request(
                self.service.users().messages().modify,
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info("Marked as read", message_id=message_id)
            return True
            
        except Exception as e:
            logger.error("Failed to mark as read", message_id=message_id, error=str(e))
            return False
    
    def mark_as_starred(self, message_id: str) -> bool:
        """
        Star an email.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            True if successful
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            self._retry_request(
                self.service.users().messages().modify,
                userId='me',
                id=message_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            
            logger.info("Marked as starred", message_id=message_id)
            return True
            
        except Exception as e:
            logger.error("Failed to mark as starred", message_id=message_id, error=str(e))
            return False
    
    def search_emails(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search emails with Gmail query syntax.
        
        Args:
            query: Gmail search query (e.g., 'from:example@email.com subject:urgent')
            max_results: Maximum results to return
            
        Returns:
            List of email dictionaries
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            logger.info("Searching emails", query=query, max_results=max_results)
            
            results = self._retry_request(
                self.service.users().messages().list,
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info("Found emails", count=len(messages))
            
            emails = []
            for message in messages:
                email_data = self._get_message_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error("Failed to search emails", error=str(e))
            raise
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get Gmail profile information.
        
        Returns:
            Profile information including email address
        """
        if not self.service:
            raise GmailAPIError("Not authenticated. Call authenticate() first.")
        
        try:
            profile = self._retry_request(
                self.service.users().getProfile,
                userId='me'
            ).execute()
            
            logger.info("Retrieved profile", email=profile.get('emailAddress'))
            return profile
            
        except Exception as e:
            logger.error("Failed to get profile", error=str(e))
            raise


def main():
    """Example usage of GmailClient."""
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Initialize client
    client = GmailClient(
        credentials_file='credentials/gmail_credentials.json',
        token_file='credentials/gmail_token.pickle'
    )
    
    # Authenticate
    print("Authenticating with Gmail...")
    client.authenticate()
    
    # Get profile
    profile = client.get_profile()
    print(f"\n✓ Authenticated as: {profile['emailAddress']}")
    
    # Fetch important emails
    print("\n📧 Fetching important emails...")
    important_emails = client.get_important_emails(max_results=5)
    
    for i, email in enumerate(important_emails, 1):
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['from']}")
        print(f"   Date: {email['date']}")
        print(f"   Snippet: {email['snippet'][:100]}...")
    
    # Fetch starred emails
    print("\n\n⭐ Fetching starred emails...")
    starred_emails = client.get_starred_emails(max_results=5)
    
    for i, email in enumerate(starred_emails, 1):
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['from']}")
        print(f"   Date: {email['date']}")
    
    print(f"\n\n✓ Total important emails: {len(important_emails)}")
    print(f"✓ Total starred emails: {len(starred_emails)}")


if __name__ == '__main__':
    main()
