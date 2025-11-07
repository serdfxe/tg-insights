from contextlib import asynccontextmanager
from .router import router, scraper

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.logging import setup_logging

from app.services.s3_session_manager import s3_manager


def init_cors(api: FastAPI) -> None:
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(api: FastAPI) -> None:
    api.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await scraper.initialize()
        print("✅ Telegram scraper initialized")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        raise

    yield

    await scraper.disconnect()


def create_api() -> FastAPI:
    api = FastAPI(
        title="Telegram Channel Scraper Service",
        description="Hide API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    init_routers(api=api)
    init_cors(api=api)

    return api


api = create_api()
setup_logging()


@api.get("/health")
async def health_check():
    """Health check with S3 status"""
    s3_status = "available" if s3_manager._initialized else "unavailable"

    return {
        "status": "healthy",
        "service": "telegram-scraper",
        "s3_storage": s3_status,
        "session_file": s3_manager.get_session_path(),
    }
