from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import commands.chat
import commands.start
import commands.help


async def create_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(commands.start.router)
    dp.include_router(commands.help.router)

    dp.include_router(commands.chat.router.router)

    return dp
