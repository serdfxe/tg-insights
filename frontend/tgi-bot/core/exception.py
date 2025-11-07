import logging

from typing import Callable, Awaitable


async def process_exception(
    exception: Exception, callback: Callable[[str], Awaitable[None]]
) -> None:
    logging.error(
        f"Exception: {exception}"
    )

    await callback("😕 Произошла внутренняя ошибка сервиса. Попробуйте позже...")
