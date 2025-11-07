from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services import resources_service


router = Router(name="start_router")


@router.message(Command("start"))
async def start_command_handler(
    message: Message,
):
    start_message = (await resources_service.get_text_resource("start")).format(
        user=message.from_user.first_name
    )
    await message.answer(start_message)
