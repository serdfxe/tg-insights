import os
from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
API_HOST: str = os.environ.get("APP_HOST", "0.0.0.0")
API_PORT: int = int(os.environ.get("APP_PORT", "8000"))
DB_URL: str = os.environ.get("DB_URL")
TELEGRAM_API_ID: str = os.environ.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH: str = os.environ.get("TELEGRAM_API_HASH")

S3_ENDPOINT_URL: str = os.environ.get("S3_ENDPOINT_URL", "https://s3.amazonaws.com")
S3_ACCESS_KEY_ID: str = os.environ.get("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY: str = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "telegram-sessions")
S3_SESSION_KEY: str = os.environ.get("S3_SESSION_KEY", "telegram_scraper.session")
S3_REGION: str = os.environ.get("S3_REGION", "us-east-1")

LOCAL_SESSION_PATH: str = os.environ.get(
    "LOCAL_SESSION_PATH", "sessions/telegram_scraper.session"
)
