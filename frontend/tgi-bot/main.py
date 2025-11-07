import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

import config
from commands import create_dispatcher
from core.exception import process_exception
from core.health import init_health


async def main() -> None:
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await init_health()

    dp = await create_dispatcher()

    @dp.error()
    async def error_handler(event: ErrorEvent):
        async def send_message(msg: str):
            await event.update.message.answer(msg)

        await process_exception(event.exception, send_message)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())