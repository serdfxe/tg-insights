from .tgi_scraper.telegram_channel_scraper_service_client import Client as ScraperClient

from config import SCRAPER_URL

scraper_client = ScraperClient(base_url=SCRAPER_URL, raise_on_unexpected_status=True, timeout=3000.0)
