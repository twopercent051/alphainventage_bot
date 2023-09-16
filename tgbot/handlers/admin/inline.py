from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class InlineKeyboard:

    def __init__(self):
        self._home_button = InlineKeyboardButton(text="🏡 На главную", callback_data="home")

    def home_kb(self):
        keyboard = [[self._home_button]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def main_menu_kb():
        keyboard = [
            [InlineKeyboardButton(text="📈 Тикеры", callback_data="tickers")],
            [InlineKeyboardButton(text="🧑‍💻 Процессы", callback_data="processes")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
