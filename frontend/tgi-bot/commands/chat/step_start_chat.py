from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .state import ChatStates

from .router import router


@router.message(Command("chat"))
async def step_start_digest(
    message: Message, state: FSMContext,
):
    await state.set_state(ChatStates.waiting_for_channel_url)
    await message.answer("Введите ссылку на телеграм канал:")
