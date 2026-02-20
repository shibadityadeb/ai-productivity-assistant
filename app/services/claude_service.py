from typing import List, Dict, Any, Optional
import os
from anthropic import Anthropic
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeService:
    """Service for interacting with Anthropic's Claude API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[Anthropic] = None
        
        if self.settings.claude_api_key:
            # Initialize directly with API key to avoid proxy configuration issues
            os.environ["ANTHROPIC_API_KEY"] = self.settings.claude_api_key
            self.client = Anthropic()
    
    async def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 1024,
        temperature: float = 1.0,
        system: Optional[str] = None
    ) -> str:
        """Generate a response from Claude."""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        try:
            message = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "You are a helpful AI assistant for productivity tasks.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Generated Claude response ({len(response_text)} chars)")
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to generate Claude response: {str(e)}")
            raise
    
    async def analyze_emails(self, emails: List[Dict[str, Any]]) -> str:
        """Analyze emails and provide insights."""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        try:
            # Format emails for analysis
            email_summaries = "\n\n".join([
                f"From: {email.get('from', 'Unknown')}\n"
                f"Subject: {email.get('subject', 'No subject')}\n"
                f"Preview: {email.get('snippet', '')[:200]}"
                for email in emails[:10]
            ])
            
            prompt = f"""Analyze the following emails and provide:
1. A brief summary of key themes
2. Any urgent items that need attention
3. Suggested actions or priorities

Emails:
{email_summaries}
"""
            
            return await self.generate_response(prompt, max_tokens=2048)
            
        except Exception as e:
            logger.error(f"Failed to analyze emails: {str(e)}")
            raise
    
    async def summarize_slack_conversations(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize Slack conversations."""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        try:
            # Format messages
            conversation = "\n".join([
                f"{msg.get('user', 'User')}: {msg.get('text', '')}"
                for msg in messages[:20]
            ])
            
            prompt = f"""Summarize the following Slack conversation. Highlight:
1. Main topics discussed
2. Key decisions or action items
3. Important questions that need answering

Conversation:
{conversation}
"""
            
            return await self.generate_response(prompt, max_tokens=1024)
            
        except Exception as e:
            logger.error(f"Failed to summarize Slack conversation: {str(e)}")
            raise
    
    async def suggest_time_tracking(self, context: str) -> str:
        """Suggest time tracking entries based on context."""
        if not self.client:
            raise ValueError("Claude client not initialized")
        
        try:
            prompt = f"""Based on the following work context, suggest appropriate time tracking entries:

Context: {context}

Provide 3-5 suggested time entries with:
- Brief description
- Estimated duration
- Suggested tags

Format as a simple list.
"""
            
            return await self.generate_response(prompt, max_tokens=512)
            
        except Exception as e:
            logger.error(f"Failed to suggest time tracking: {str(e)}")
            raise
