from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Gmail Schemas
class EmailMessage(BaseModel):
    to: EmailStr
    subject: str
    body: str


class EmailQuery(BaseModel):
    max_results: int = Field(default=10, ge=1, le=100)
    query: Optional[str] = None


# Slack Schemas
class SlackMessage(BaseModel):
    channel: str
    text: str
    blocks: Optional[List[dict]] = None


class SlackChannelHistory(BaseModel):
    channel: str
    limit: int = Field(default=10, ge=1, le=100)


# Toggl Schemas
class TimeEntryCreate(BaseModel):
    description: str
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None


class TimeEntryQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# AI Schemas
class AIPrompt(BaseModel):
    prompt: str
    max_tokens: int = Field(default=1024, ge=100, le=4096)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    system: Optional[str] = None


class EmailAnalysisRequest(BaseModel):
    emails: List[dict]


class SlackSummaryRequest(BaseModel):
    messages: List[dict]


class ProductivityAnalysisRequest(BaseModel):
    time_entries: List[dict]


class DailySummaryRequest(BaseModel):
    emails: List[dict] = []
    slack_messages: List[dict] = []
    time_entries: List[dict] = []


class SmartReplyRequest(BaseModel):
    message: str
    context: Optional[str] = None


# Response Schemas
class StatusResponse(BaseModel):
    status: str
    message: str


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
