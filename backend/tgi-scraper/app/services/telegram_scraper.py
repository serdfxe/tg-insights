from datetime import datetime
import logging
from typing import Any

from telethon import TelegramClient
from telethon.tl.types import (
    Message,
    MessageMediaPhoto,
    MessageMediaDocument,
)
from telethon.errors import (
    FloodWaitError,
    ChannelPrivateError,
    UsernameNotOccupiedError,
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest

from core.config import TELEGRAM_API_ID, TELEGRAM_API_HASH
from db.models.stats import ChannelStats, MessageStats
from db.uow import get_uow

from app.services.s3_session_manager import s3_manager


logger = logging.getLogger(__name__)


class TelegramScraper:
    def __init__(self):
        self.client: TelegramClient | None = None
        self.session_manager = s3_manager

    async def initialize(self):
        """Initialize Telegram client with S3 session management"""
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            raise ValueError("Telegram API credentials not configured")

        self.session_manager.initialize()

        await self.session_manager.download_session()

        session_path = self.session_manager.get_session_path()

        self.client = TelegramClient(
            session_path, int(TELEGRAM_API_ID), TELEGRAM_API_HASH
        )

        await self.client.connect()

        if not await self.client.is_user_authorized():
            logger.warning("Telegram client not authorized. Please authenticate.")
            raise ValueError(
                "Telegram client not authorized. Please authenticate first."
            )
        else:
            logger.info("Telegram client authorized successfully")
            await self.session_manager.upload_session()

    async def scrape_channel_stats(
        self, channel_identifier: str, limit_messages: int = 100
    ) -> dict[str, Any]:
        """Основной метод скрапинга статистики канала"""
        if not self.client:
            await self.initialize()

        try:
            entity = await self.client.get_entity(channel_identifier)

            channel_data = {
                "channel_id": entity.id,
                "username": getattr(entity, "username", None),
                "title": getattr(
                    entity, "title", getattr(entity, "first_name", "Unknown")
                ),
            }

            try:
                if hasattr(entity, "broadcast") and entity.broadcast:
                    full_channel = await self.client(GetFullChannelRequest(entity))
                    channel_data.update(
                        {
                            "subscribers_count": getattr(
                                full_channel.full_chat, "participants_count", None
                            ),
                            "description": getattr(
                                full_channel.full_chat, "about", None
                            ),
                            "participants_count": getattr(
                                full_channel.full_chat, "participants_count", None
                            ),
                        }
                    )
                else:
                    full_chat = await self.client(GetFullChatRequest(entity.id))
                    channel_data.update(
                        {
                            "subscribers_count": getattr(
                                full_chat.full_chat, "participants_count", None
                            ),
                            "description": getattr(full_chat.full_chat, "about", None),
                            "participants_count": getattr(
                                full_chat.full_chat, "participants_count", None
                            ),
                        }
                    )
            except Exception as e:
                logger.warning(f"Could not get full channel info: {e}")
                channel_data.update(
                    {
                        "subscribers_count": getattr(
                            entity, "participants_count", None
                        ),
                        "participants_count": getattr(
                            entity, "participants_count", None
                        ),
                        "description": getattr(entity, "about", None),
                    }
                )

            messages_data = []
            total_views = 0
            total_reactions = 0
            total_forwards = 0
            messages_with_stats = 0

            async for message in self.client.iter_messages(
                entity, limit=limit_messages
            ):
                if not isinstance(message, Message):
                    continue

                message_stats = await self._extract_message_stats(message)
                messages_data.append(message_stats)

                if message_stats["views"]:
                    total_views += message_stats["views"]
                    messages_with_stats += 1

                total_forwards += message_stats["forwards"] or 0
                total_reactions += sum(message_stats["reactions"].values())

            await self._save_to_database(
                channel_data,
                messages_data,
                total_views,
                total_forwards,
                total_reactions,
                messages_with_stats,
            )

            messages_response = []
            for msg in messages_data:
                messages_response.append(
                    {
                        "message_id": msg["message_id"],
                        "date": msg["date"],
                        "views": msg["views"],
                        "forwards": msg["forwards"],
                        "replies": msg["replies"],
                        "reactions": msg["reactions"],
                        "text": msg["text"],
                        "media_type": msg["media_type"],
                        "has_media": msg["has_media"],
                    }
                )

            await self.session_manager.upload_session()

            return {
                "channel_id": channel_data["channel_id"],
                "username": channel_data["username"],
                "title": channel_data["title"],
                "description": channel_data.get("description"),
                "subscribers_count": channel_data["subscribers_count"],
                "participants_count": channel_data["participants_count"],
                "messages": messages_response,
            }

        except (ChannelPrivateError, UsernameNotOccupiedError) as e:
            raise ValueError(f"Channel error: {str(e)}")
        except FloodWaitError as e:
            raise ValueError(f"Flood wait: {e.seconds} seconds")
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            raise ValueError(f"Scraping failed: {str(e)}")

    async def _extract_message_stats(self, message: Message) -> dict[str, Any]:
        """Извлекает статистику из сообщения"""
        reactions = {}
        if message.reactions:
            if hasattr(message.reactions, "results"):
                for reaction in message.reactions.results:
                    if hasattr(reaction, "count"):
                        reaction_key = self._get_reaction_key(reaction)
                        reactions[reaction_key] = reaction.count

        replies_count = 0
        if message.replies:
            if hasattr(message.replies, "replies"):
                replies_count = message.replies.replies
            elif hasattr(message.replies, "replies_count"):
                replies_count = message.replies.replies_count

        media_type = None
        has_media = 0
        if message.media:
            has_media = 1
            if isinstance(message.media, MessageMediaPhoto):
                media_type = "photo"
            elif isinstance(message.media, MessageMediaDocument):
                media_type = "document"

        message_date = message.date
        if message_date.tzinfo is not None:
            message_date = message_date.replace(tzinfo=None)

        return {
            "message_id": message.id,
            "date": message_date,
            "views": getattr(message, "views", None),
            "forwards": getattr(message, "forwards", None),
            "replies": replies_count,
            "reactions": reactions,
            "text": message.text or "",
            "media_type": media_type,
            "has_media": has_media,
        }

    def _get_reaction_key(self, reaction) -> str:
        """Получает ключ для реакции"""
        if hasattr(reaction.reaction, "emoticon") and reaction.reaction.emoticon:
            return reaction.reaction.emoticon
        elif hasattr(reaction.reaction, "document_id"):
            return f"document_{reaction.reaction.document_id}"
        else:
            return str(reaction.reaction)

    async def _save_to_database(
        self,
        channel_data: dict,
        messages_data: list[dict],
        total_views: int,
        total_forwards: int,
        total_reactions: int,
        messages_with_stats: int,
    ):
        """Сохраняет данные в базу"""
        async with get_uow() as uow:
            channel_stats_repo = await uow.get_repo(ChannelStats)
            message_stats_repo = await uow.get_repo(MessageStats)

            avg_views = (
                total_views / messages_with_stats if messages_with_stats > 0 else 0
            )
            avg_reactions = total_reactions / len(messages_data) if messages_data else 0
            avg_forwards = total_forwards / len(messages_data) if messages_data else 0

            await channel_stats_repo.create(
                {
                    "channel_id": channel_data["channel_id"],
                    "username": channel_data["username"],
                    "title": channel_data["title"],
                    "scraped_at": datetime.now(),
                    "subscribers_count": channel_data["subscribers_count"],
                    "participants_count": channel_data["participants_count"],
                    "description": channel_data.get("description", "")[:500],
                    "total_messages": len(messages_data),
                    "avg_views": int(avg_views),
                    "avg_reactions": int(avg_reactions),
                    "avg_forwards": int(avg_forwards),
                    "messages_analyzed": len(messages_data),
                    "recent_activity": {
                        "last_scrape": datetime.now().isoformat(),
                        "messages_count": len(messages_data),
                    },
                }
            )

            for msg_data in messages_data:
                await message_stats_repo.create(
                    {
                        "channel_id": channel_data["channel_id"],
                        "message_id": msg_data["message_id"],
                        "date": msg_data["date"],
                        "scraped_at": datetime.now(),
                        "views": msg_data["views"],
                        "forwards": msg_data["forwards"],
                        "replies": msg_data["replies"],
                        "reactions": msg_data["reactions"],
                        "text": (msg_data["text"] or "")[:1000],
                        "media_type": msg_data["media_type"],
                        "has_media": msg_data["has_media"],
                    }
                )

            await uow.commit()
            logger.info(
                f"Saved {len(messages_data)} messages for channel {channel_data['channel_id']}"
            )

    async def get_channel_history(self, channel_id: int, limit: int = 10):
        """Получает историю статистики канала"""
        async with get_uow() as uow:
            repo = await uow.get_repo(ChannelStats)
            stats = await repo.filter(ChannelStats.channel_id == channel_id)
            stats = sorted(stats, key=lambda x: x.scraped_at, reverse=True)[:limit]
            return stats

    async def disconnect(self):
        """Отключает клиент и сохраняет сессию в S3"""
        if self.client:
            await self.session_manager.upload_session()
            await self.client.disconnect()
            logger.info("Telegram client disconnected and session saved to S3")
