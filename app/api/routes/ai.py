from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.services.claude_service import ClaudeService
from app.services.gemini_service import GeminiService
from app.models.schemas import (
    AIPrompt, EmailAnalysisRequest, SlackSummaryRequest,
    ProductivityAnalysisRequest, DailySummaryRequest, SmartReplyRequest
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai", tags=["AI"])


def get_claude_service() -> ClaudeService:
    """Dependency for Claude service."""
    return ClaudeService()


def get_gemini_service() -> GeminiService:
    """Dependency for Gemini service."""
    return GeminiService()


@router.post("/claude/generate")
async def claude_generate(
    prompt: AIPrompt,
    service: ClaudeService = Depends(get_claude_service)
) -> Dict[str, Any]:
    """Generate a response using Claude."""
    try:
        response = await service.generate_response(
            prompt=prompt.prompt,
            max_tokens=prompt.max_tokens,
            temperature=prompt.temperature,
            system=prompt.system
        )
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Failed to generate Claude response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/claude/analyze-emails")
async def analyze_emails(
    request: EmailAnalysisRequest,
    service: ClaudeService = Depends(get_claude_service)
) -> Dict[str, Any]:
    """Analyze emails with Claude."""
    try:
        analysis = await service.analyze_emails(request.emails)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Failed to analyze emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/claude/summarize-slack")
async def summarize_slack(
    request: SlackSummaryRequest,
    service: ClaudeService = Depends(get_claude_service)
) -> Dict[str, Any]:
    """Summarize Slack conversations with Claude."""
    try:
        summary = await service.summarize_slack_conversations(request.messages)
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to summarize Slack: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gemini/generate")
async def gemini_generate(
    prompt: AIPrompt,
    service: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """Generate a response using Gemini."""
    try:
        response = await service.generate_response(
            prompt=prompt.prompt,
            max_output_tokens=prompt.max_tokens,
            temperature=prompt.temperature
        )
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Failed to generate Gemini response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gemini/analyze-productivity")
async def analyze_productivity(
    request: ProductivityAnalysisRequest,
    service: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """Analyze productivity with Gemini."""
    try:
        analysis = await service.analyze_productivity(request.time_entries)
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Failed to analyze productivity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gemini/daily-summary")
async def daily_summary(
    request: DailySummaryRequest,
    service: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """Generate daily summary with Gemini."""
    try:
        summary = await service.generate_daily_summary(
            emails=request.emails,
            slack_messages=request.slack_messages,
            time_entries=request.time_entries
        )
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gemini/smart-reply")
async def smart_reply(
    request: SmartReplyRequest,
    service: GeminiService = Depends(get_gemini_service)
) -> Dict[str, Any]:
    """Generate smart reply suggestions with Gemini."""
    try:
        replies = await service.smart_reply(
            message=request.message,
            context=request.context
        )
        return {
            "status": "success",
            "replies": replies
        }
    except Exception as e:
        logger.error(f"Failed to generate smart replies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
