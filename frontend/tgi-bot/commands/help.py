from aiogram import Router
from aiogram.filters import Command

from services import resources_service


router = Router(name="help_router")


@router.message(Command("help"))
async def help_command_handler(message):
    await message.answer(
        await resources_service.get_text_resource("help"), parse_mode="HTML"
    )
