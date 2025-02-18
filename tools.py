from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
        """
        Создаем клавиатуру с кнопками от 1 до 10, размещёнными в 2 ряда по 5 кнопок,
        а также ряд с кнопкой «Back».
        """
        buttons = [KeyboardButton(text=str(i)) for i in range(1, 11)]
        row1 = buttons[:5]
        row2 = buttons[5:]
        back_text = texts.get(lang, {}).get("back", "Back")
        row3 = [KeyboardButton(text=back_text)]
        return ReplyKeyboardMarkup(keyboard=[row1, row2, row3],
                                   resize_keyboard=True)

    @classmethod
    def get_history_markup(cls, items: list, lang: str):
        """
        Здесь оставляем инлайн‑клавиатуру для истории каппинга (без изменений).
        items – список кортежей: (cupping_id, brewing_method, avg)
        """
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        rows = []
        for item in items:
            btn_text = f"#{item[0]} | {item[1]} | {item[2]:.1f}"
            rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"history_{item[0]}")])
        menu_text = texts.get(lang, {}).get("menu", "Menu")
        rows.append([InlineKeyboardButton(text=menu_text, callback_data="to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    @classmethod
    def get_note_back_markup(cls, lang: str):
        back_text = texts.get(lang, {}).get("back", "Back")
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_text)]],
                                   resize_keyboard=True)
