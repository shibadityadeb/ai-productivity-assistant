from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
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
        is_authenticated = service.authenticate()
        return {
            "status": "authenticated" if is_authenticated else "not_authenticated",
            "message": "Gmail is authenticated" if is_authenticated else "Authentication required"
        }
    except Exception as e:
        logger.error(f"Failed to check auth status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
