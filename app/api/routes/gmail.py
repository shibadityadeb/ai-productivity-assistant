from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.services.gmail_service import GmailService
from app.models.schemas import EmailMessage, EmailQuery
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/gmail", tags=["Gmail"])


def get_gmail_service() -> GmailService:
    """Dependency for Gmail service."""
    return GmailService()


@router.get("/messages")
async def list_messages(
    query: EmailQuery = Depends(),
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """List recent email messages."""
    try:
        messages = await service.list_messages(
            max_results=query.max_results,
            query=query.query or ""
        )
        return {
            "status": "success",
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Failed to list messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{message_id}")
async def get_message(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Get a specific email message."""
    try:
        message = await service.get_message(message_id)
        return {
            "status": "success",
            "message": message
        }
    except Exception as e:
        logger.error(f"Failed to get message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(
    email: EmailMessage,
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Send an email message."""
    try:
        result = await service.send_message(
            to=email.to,
            subject=email.subject,
            body=email.body
        )
        return {
            "status": "success",
            "message": "Email sent successfully",
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/status")
async def auth_status(
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Check Gmail authentication status."""
    try:
        profile = await service.get_profile()
        return {
            "status": "authenticated",
            "email": profile.get('emailAddress'),
            "messages_total": profile.get('messagesTotal'),
            "threads_total": profile.get('threadsTotal')
        }
    except Exception as e:
        logger.error(f"Failed to check auth status: {str(e)}")
        return {
            "status": "not_authenticated",
            "message": str(e)
        }


@router.get("/important")
async def get_important_emails(
    max_results: int = Query(default=10, ge=1, le=50),
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Get important emails."""
    try:
        emails = await service.get_important_emails(max_results)
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        logger.error(f"Failed to get important emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/starred")
async def get_starred_emails(
    max_results: int = Query(default=10, ge=1, le=50),
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Get starred emails."""
    try:
        emails = await service.get_starred_emails(max_results)
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        logger.error(f"Failed to get starred emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread")
async def get_unread_emails(
    max_results: int = Query(default=20, ge=1, le=100),
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Get unread emails."""
    try:
        emails = await service.get_unread_emails(max_results)
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        logger.error(f"Failed to get unread emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_emails(
    q: str = Query(..., description="Gmail search query"),
    max_results: int = Query(default=20, ge=1, le=100),
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """
    Search emails with Gmail query syntax.
    
    Examples:
    - from:user@example.com
    - subject:urgent is:unread
    - has:attachment larger:5M
    """
    try:
        emails = await service.search_emails(q, max_results)
        return {
            "status": "success",
            "query": q,
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard(
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Get email dashboard with summary statistics."""
    try:
        # Fetch various email categories
        important = await service.get_important_emails(max_results=10)
        starred = await service.get_starred_emails(max_results=10)
        unread = await service.get_unread_emails(max_results=50)
        
        # Calculate statistics
        from collections import Counter
        
        senders = [email.get('from', '') for email in unread]
        top_senders = Counter(senders).most_common(5)
        
        return {
            "status": "success",
            "summary": {
                "important_count": len(important),
                "starred_count": len(starred),
                "unread_count": len(unread)
            },
            "top_senders": [
                {"sender": sender, "count": count} 
                for sender, count in top_senders
            ],
            "recent_important": [
                {
                    "id": email.get('id'),
                    "subject": email.get('subject'),
                    "from": email.get('from'),
                    "date": email.get('date'),
                    "is_unread": email.get('is_unread', False),
                    "snippet": email.get('snippet', '')[:100]
                }
                for email in important[:5]
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/read")
async def mark_as_read(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Mark an email as read."""
    try:
        success = await service.mark_as_read(message_id)
        return {
            "status": "success" if success else "failed",
            "message_id": message_id
        }
    except Exception as e:
        logger.error(f"Failed to mark as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/{message_id}/star")
async def mark_as_starred(
    message_id: str,
    service: GmailService = Depends(get_gmail_service)
) -> Dict[str, Any]:
    """Star an email."""
    try:
        success = await service.mark_as_starred(message_id)
        return {
            "status": "success" if success else "failed",
            "message_id": message_id
        }
    except Exception as e:
        logger.error(f"Failed to mark as starred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
