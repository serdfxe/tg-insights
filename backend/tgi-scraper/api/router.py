from fastapi import HTTPException, APIRouter
from app.services.telegram_scraper import TelegramScraper
from app.schemas.stats import ScrapeRequest, ScrapeResponse


router = APIRouter(prefix="", tags=["channels"])
scraper = TelegramScraper()


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_channel_route(request: ScrapeRequest):
    """Scrape channel statistics. The operation collects and returns current channel metrics including subscribers, views, and engagement data."""
    try:
        result = await scraper.scrape_channel_stats(
            request.channel_identifier, request.limit_messages
        )
        return ScrapeResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/{channel_id}")
async def get_channel_stats_route(channel_id: int, limit: int = 5):
    """Get channel statistics history. The operation returns historical metrics for the specified channel including subscriber growth and engagement trends."""
    try:
        stats = await scraper.get_channel_history(channel_id, limit)
        return {
            "channel_id": channel_id,
            "history": [
                {
                    "scraped_at": stat.scraped_at,
                    "subscribers_count": stat.subscribers_count,
                    "avg_views": stat.avg_views,
                    "avg_reactions": stat.avg_reactions,
                    "total_messages": stat.total_messages,
                }
                for stat in stats
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
