from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class Keyboard:
    def __init__(self, row_width: int = 2):
        self.row_width = row_width
        self.buttons = []
        self.row_breaks = set()

    def add_button(
        self, label: str, callback: str, new_row: bool = False
    ) -> "Keyboard":
        if new_row:
            self.row_breaks.add(len(self.buttons) - 1)

        self.buttons.append(InlineKeyboardButton(text=label, callback_data=callback))
        return self

    def add_row_break(self) -> "Keyboard":
        if self.buttons:
            self.row_breaks.add(len(self.buttons) - 1)
        return self

    def build(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        if not self.buttons:
            return keyboard

        current_row = []

        for i, button in enumerate(self.buttons):
            current_row.append(button)
            if (
                len(current_row) >= self.row_width
                or i in self.row_breaks
                or i == len(self.buttons) - 1
            ):

                keyboard.inline_keyboard.append(current_row)
                current_row = []

        return keyboard


SKIP_KEYBOARD = Keyboard().add_button("Пропустить", "skip").build()
