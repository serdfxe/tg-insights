from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    channel_identifier: str
    limit_messages: int = 100


class MessageStatsResponse(BaseModel):
    message_id: int
    date: datetime
    views: Optional[int]
    forwards: Optional[int]
    replies: Optional[int]
    reactions: Dict[str, int]
    text: str
    media_type: Optional[str]
    has_media: bool


class ScrapeResponse(BaseModel):
    channel_id: int
    username: Optional[str]
    title: str
    description: Optional[str]
    subscribers_count: Optional[int]
    participants_count: Optional[int]
    messages: List[MessageStatsResponse]


class ChannelStatsResponse(BaseModel):
    channel_id: int
    username: Optional[str]
    title: str
    subscribers_count: Optional[int]
    participants_count: Optional[int]
    total_messages: int
    avg_views: Optional[float]
    avg_reactions: Optional[float]
    scraped_at: datetime
