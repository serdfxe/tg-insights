from uuid import uuid4
from sqlalchemy import Column, UUID, String, Integer, DateTime, Text, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChannelStats(Base):
    __tablename__ = "channel_stats"

    id = Column(UUID, primary_key=True, default=uuid4)
    channel_id = Column(BigInteger, nullable=False)
    username = Column(String(255))
    title = Column(String(500), nullable=False)
    scraped_at = Column(DateTime, nullable=False)

    subscribers_count = Column(Integer)
    participants_count = Column(Integer)
    description = Column(Text)
    photo_url = Column(String(500))

    total_messages = Column(Integer)
    avg_views = Column(Integer)
    avg_reactions = Column(Integer)
    avg_forwards = Column(Integer)

    messages_analyzed = Column(Integer)
    recent_activity = Column(JSON)


class MessageStats(Base):
    __tablename__ = "message_stats"

    id = Column(UUID, primary_key=True, default=uuid4)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    date = Column(DateTime, nullable=False)
    scraped_at = Column(DateTime, nullable=False)

    views = Column(Integer)
    forwards = Column(Integer)
    replies = Column(Integer)
    reactions = Column(JSON)

    text = Column(Text)
    media_type = Column(String(100))
    has_media = Column(Integer)
