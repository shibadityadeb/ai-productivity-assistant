from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        
        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.model = genai.GenerativeModel(self.settings.gemini_model)
    
    async def generate_response(
        self, 
        prompt: str,
        temperature: float = 1.0,
        max_output_tokens: int = 1024
    ) -> str:
        """Generate a response from Gemini."""
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text
            logger.info(f"Generated Gemini response ({len(response_text)} chars)")
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to generate Gemini response: {str(e)}")
            raise
    
    async def analyze_productivity(self, time_entries: List[Dict[str, Any]]) -> str:
        """Analyze productivity from time tracking data."""
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            # Format time entries
            entries_summary = "\n".join([
                f"- {entry.get('description', 'Unknown')}: {entry.get('duration', 0) / 3600:.2f}h"
                for entry in time_entries[:20]
            ])
            
            prompt = f"""Analyze the following time tracking data and provide:
1. Productivity patterns
2. Time allocation by category
3. Suggestions for optimization

Time Entries:
{entries_summary}

Provide actionable insights.
"""
            
            return await self.generate_response(prompt, max_output_tokens=2048)
            
        except Exception as e:
            logger.error(f"Failed to analyze productivity: {str(e)}")
            raise
    
    async def generate_daily_summary(
        self, 
        emails: List[Dict[str, Any]], 
        slack_messages: List[Dict[str, Any]],
        time_entries: List[Dict[str, Any]]
    ) -> str:
        """Generate a daily productivity summary."""
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            prompt = f"""Create a daily productivity summary based on:

Emails: {len(emails)} emails received
Slack: {len(slack_messages)} messages
Time Tracked: {len(time_entries)} entries

Provide:
1. Overview of the day's activities
2. Key communications
3. Time allocation
4. Tomorrow's priorities

Keep it concise and actionable.
"""
            
            return await self.generate_response(prompt, max_output_tokens=1024)
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {str(e)}")
            raise
    
    async def smart_reply(self, message: str, context: str = "") -> List[str]:
        """Generate smart reply suggestions."""
        if not self.model:
            raise ValueError("Gemini model not initialized")
        
        try:
            prompt = f"""Generate 3 brief, professional reply suggestions for this message:

Message: {message}

{f'Context: {context}' if context else ''}

Provide 3 short replies (1-2 sentences each), numbered.
"""
            
            response = await self.generate_response(prompt, max_output_tokens=256)
            
            # Parse replies
            replies = [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line[:3])]
            return replies[:3]
            
        except Exception as e:
            logger.error(f"Failed to generate smart replies: {str(e)}")
            raise
