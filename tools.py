# tools.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
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
        # Create an inline keyboard for rating from 1 to 10 in two rows and a third row with a 'Back' button.
        keyboard = InlineKeyboardMarkup(row_width=5)
        buttons = [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 11)]
        keyboard.add(*buttons[0:5])
        keyboard.add(*buttons[5:10])
        back_text = texts.get(lang, {}).get("back", "Back")
        keyboard.add(InlineKeyboardButton(text=back_text, callback_data="back"))
        return keyboard

    @classmethod
    def get_history_markup(cls, items: list, lang: str):
        # items: list of tuples (cupping_id, brewing_method, avg)
        keyboard = InlineKeyboardMarkup(row_width=1)
        for item in items:
            btn_text = f"#{item[0]} | {item[1]} | {item[2]:.1f}"
            keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"history_{item[0]}"))
        menu_text = texts.get(lang, {}).get("menu", "Menu")
        keyboard.add(InlineKeyboardButton(text=menu_text, callback_data="to_menu"))
        return keyboard

    @classmethod
    def get_note_back_markup(cls, lang: str):
        back_text = texts.get(lang, {}).get("back", "Back")
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_text)]],
                                   resize_keyboard=True)
