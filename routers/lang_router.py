from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from FSMachines import CandidateState
from tools import Tools
from bot_dictionary import texts
from loguru import logger

lang_router = Router()


@lang_router.message()
async def language_handler(msg: Message, state: FSMContext):
    if msg.text not in ["EN", "RU", "UA"]:
        return
    lang = msg.text
    await state.update_data(language=lang)
    logger.info(f"User {msg.from_user.id} set language: {lang}")
    markup = Tools.get_menu_markup(lang)
    await msg.answer(texts.get(lang, {}).get("welcome", "Welcome!"), reply_markup=markup)
    await state.clear()
