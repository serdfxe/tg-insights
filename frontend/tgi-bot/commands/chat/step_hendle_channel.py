from io import BytesIO
import json
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from core.tgi_clients import scraper_client
from core.tgi_clients.tgi_scraper.telegram_channel_scraper_service_client.api.channels import scrape_channel_scrape_post
from core.tgi_clients.tgi_scraper.telegram_channel_scraper_service_client.models import ScrapeResponse, ScrapeRequest

from .state import ChatStates

from .router import router


@router.message(ChatStates.waiting_for_channel_url)
async def channel_hendler(
    message: Message, state: FSMContext,
):
    await state.clear()

    channel = message.text.replace("@", "").replace("https://t.me/", "").strip()

    data: ScrapeResponse = await scrape_channel_scrape_post.asyncio(
        client=scraper_client,
        body=ScrapeRequest(
            channel_identifier=channel
        )
    )

    json_text = json.dumps(data.to_dict(), indent=2, ensure_ascii=False)

    json_file = BufferedInputFile(
        file=json_text.encode('utf-8'),
        filename='data.json'
    )

    await message.answer_document(
        document=json_file,
        caption=f"Файл со статистикой канала @{channel}"
    )
