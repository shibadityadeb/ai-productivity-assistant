from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
from app.services.gmail_service import GmailService
from app.services.claude_service import ClaudeService
from app.services.gemini_service import GeminiService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/productivity", tags=["Productivity"])


def get_gmail_service() -> GmailService:
    """Dependency for Gmail service."""
    return GmailService()


def get_claude_service() -> ClaudeService:
    """Dependency for Claude service."""
    return ClaudeService()


def get_gemini_service() -> GeminiService:
    """Dependency for Gemini service."""
    return GeminiService()


@router.get("/email-summary")
async def get_email_summary(
    max_emails: int = Query(default=20, ge=5, le=50),
    use_ai: str = Query(default="claude", regex="^(claude|gemini)$"),
    gmail: GmailService = Depends(get_gmail_service),
    claude: ClaudeService = Depends(get_claude_service),
    gemini: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """
    Get AI-powered email summary and insights.
    
    Uses Claude or Gemini to analyze your emails and provide:
    - Key themes and topics
    - Urgent items requiring attention
    - Suggested priorities
    """
    try:
        # Fetch recent important and unread emails
        important = await gmail.get_important_emails(max_results=max_emails // 2)
        unread = await gmail.get_unread_emails(max_results=max_emails // 2)
        
        # Combine and deduplicate
        all_emails = important + unread
        seen_ids = set()
        unique_emails = []
        for email in all_emails:
            if email['id'] not in seen_ids:
                unique_emails.append(email)
                seen_ids.add(email['id'])
        
        if not unique_emails:
            return {
                "status": "success",
                "message": "No emails to analyze",
                "summary": None
            }
        
        # Prepare email data for AI analysis
        email_data = [
            {
                "from": email.get('from', 'Unknown'),
                "subject": email.get('subject', 'No subject'),
                "snippet": email.get('snippet', ''),
                "is_unread": email.get('is_unread', False),
                "is_important": email.get('is_important', False)
            }
            for email in unique_emails[:max_emails]
        ]
        
        # Get AI analysis
        if use_ai == "claude":
            analysis = await claude.analyze_emails(email_data)
        else:
            analysis = await gemini.generate_response(
                f"Analyze these emails and provide: 1) Key themes, 2) Urgent items, 3) Priorities\\n\\n{str(email_data)}",
                max_output_tokens=2048
            )
        
        return {
            "status": "success",
            "ai_model": use_ai,
            "emails_analyzed": len(unique_emails),
            "summary": analysis,
            "email_counts": {
                "total": len(unique_emails),
                "unread": sum(1 for e in unique_emails if e.get('is_unread')),
                "important": sum(1 for e in unique_emails if e.get('is_important'))
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate email summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inbox-insights")
async def get_inbox_insights(
    gmail: GmailService = Depends(get_gmail_service),
    gemini: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """
    Get AI-powered inbox insights and productivity recommendations.
    
    Analyzes your email patterns and provides actionable insights.
    """
    try:
        # Fetch emails
        important = await gmail.get_important_emails(max_results=20)
        unread = await gmail.get_unread_emails(max_results=50)
        starred = await gmail.get_starred_emails(max_results=10)
        
        # Calculate statistics
        from collections import Counter
        from datetime import datetime
        
        # Sender analysis
        senders = [email.get('from', '') for email in unread]
        top_senders = Counter(senders).most_common(5)
        
        # Time analysis (if dates available)
        unread_by_age = {
            "today": 0,
            "this_week": 0,
            "older": 0
        }
        
        # Prepare summary for AI
        summary_text = f"""
        Email Statistics:
        - Unread: {len(unread)}
        - Important: {len(important)}
        - Starred: {len(starred)}
        
        Top Senders (unread):
        {chr(10).join([f"- {sender}: {count} emails" for sender, count in top_senders])}
        
        Recent Important Subjects:
        {chr(10).join([f"- {email.get('subject', 'No subject')}" for email in important[:5]])}
        """
        
        # Get AI insights
        insights = await gemini.generate_response(
            f"Based on this inbox data, provide: 1) Productivity insights, 2) Email management recommendations, 3) Action items\\n\\n{summary_text}",
            max_output_tokens=1024
        )
        
        return {
            "status": "success",
            "statistics": {
                "unread_count": len(unread),
                "important_count": len(important),
                "starred_count": len(starred),
                "top_senders": [
                    {"sender": sender, "count": count}
                    for sender, count in top_senders
                ]
            },
            "ai_insights": insights,
            "recommendations": {
                "emails_to_review": len(important),
                "estimated_time": f"{len(unread) * 2} minutes"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get inbox insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-reply")
async def generate_smart_reply(
    message_id: str,
    context: Optional[str] = None,
    gmail: GmailService = Depends(get_gmail_service),
    gemini: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """
    Generate AI-powered smart reply suggestions for an email.
    
    Args:
        message_id: Gmail message ID
        context: Optional context to influence the reply
    """
    try:
        # Fetch the email
        email = await gmail.get_message(message_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Extract email content
        message_text = f"From: {email.get('from')}\\nSubject: {email.get('subject')}\\n\\n{email.get('body', email.get('snippet', ''))}"
        
        # Generate smart replies
        replies = await gemini.smart_reply(message_text, context or "")
        
        return {
            "status": "success",
            "message_id": message_id,
            "email_subject": email.get('subject'),
            "suggested_replies": replies
        }
        
    except Exception as e:
        logger.error(f"Failed to generate smart replies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/urgent-detector")
async def detect_urgent_emails(
    max_results: int = Query(default=20, ge=5, le=50),
    gmail: GmailService = Depends(get_gmail_service),
    claude: ClaudeService = Depends(get_claude_service)
) -> Dict[str, Any]:
    """
    AI-powered urgent email detection.
    
    Analyzes unread emails and identifies which ones require immediate attention.
    """
    try:
        # Fetch unread emails
        unread = await gmail.get_unread_emails(max_results=max_results)
        
        if not unread:
            return {
                "status": "success",
                "message": "No unread emails",
                "urgent_emails": []
            }
        
        # Prepare email summaries
        email_summaries = []
        for i, email in enumerate(unread):
            email_summaries.append({
                "index": i,
                "id": email.get('id'),
                "from": email.get('from'),
                "subject": email.get('subject'),
                "snippet": email.get('snippet', '')[:200]
            })
        
        # Ask Claude to identify urgent emails
        prompt = f"""Analyze these emails and identify which ones are URGENT (require immediate attention).
        
        Consider: deadlines, requests from management, time-sensitive matters, important meetings.
        
        Emails:
        {chr(10).join([f"{i+1}. From: {e['from']} | Subject: {e['subject']}" for i, e in enumerate(email_summaries)])}
        
        Respond with ONLY the numbers of urgent emails (comma-separated) and brief reason for each.
        Format: "1 (reason), 3 (reason), 5 (reason)" or "None" if no urgent emails.
        """
        
        analysis = await claude.generate_response(prompt, max_tokens=512, temperature=0.3)
        
        return {
            "status": "success",
            "total_unread": len(unread),
            "urgent_analysis": analysis,
            "all_emails": [
                {
                    "id": email.get('id'),
                    "from": email.get('from'),
                    "subject": email.get('subject'),
                    "snippet": email.get('snippet', '')[:100]
                }
                for email in unread
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to detect urgent emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
