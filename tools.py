# tools.py
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from bot_dictionary import texts


class Tools:
    @classmethod
    def get_language_markup(cls):
        buttons = [
            KeyboardButton(text="EN"),
            KeyboardButton(text="RU"),
            KeyboardButton(text="UA")
        ]
        return ReplyKeyboardMarkup(keyboard=[[btn] for btn in buttons],
                                   resize_keyboard=True)

    @classmethod
    def get_menu_markup(cls, lang: str):
        btn_texts = texts.get(lang, {})
        buttons = [
            KeyboardButton(text=btn_texts.get("menu_start_cupping", "Start Cupping")),
            KeyboardButton(text=btn_texts.get("menu_history", "Cupping History")),
            KeyboardButton(text=btn_texts.get("menu_change_language", "Change Language"))
        ]
        return ReplyKeyboardMarkup(keyboard=[[btn] for btn in buttons],
                                   resize_keyboard=True)

    @classmethod
    def get_rating_keyboard(cls, lang: str):
        # Формируем список кнопок для оценок от 1 до 10
        number_buttons = [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 11)]
        # Разбиваем их на два ряда по 5 кнопок
        row1 = number_buttons[0:5]
        row2 = number_buttons[5:10]
        back_text = texts.get(lang, {}).get("back", "Back")
        row3 = [InlineKeyboardButton(text=back_text, callback_data="back")]
        # Явно передаем двумерный список в inline_keyboard
        keyboard = InlineKeyboardMarkup(inline_keyboard=[row1, row2, row3], row_width=5)
        return keyboard

    @classmethod
    def get_history_markup(cls, items: list, lang: str):
        # items: список кортежей (cupping_id, brewing_method, avg)
        rows = []
        for item in items:
            btn_text = f"#{item[0]} | {item[1]} | {item[2]:.1f}"
            rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"history_{item[0]}")])
        menu_text = texts.get(lang, {}).get("menu", "Menu")
        rows.append([InlineKeyboardButton(text=menu_text, callback_data="to_menu")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
        return keyboard

    @classmethod
    def get_note_back_markup(cls, lang: str):
        back_text = texts.get(lang, {}).get("back", "Back")
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_text)]],
                                   resize_keyboard=True)
