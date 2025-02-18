from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from FSMachines import CandidateState, AppState
from tools import Tools
from bot_dictionary import texts
from loguru import logger

lang_router = Router()

@lang_router.message(lambda message: message.text in ["EN", "RU", "UA"])
async def language_handler(msg: Message, state: FSMContext):
    lang = msg.text
    # Сохраняем выбранный язык в состоянии
    await state.update_data(language=lang)
    logger.info(f"User {msg.from_user.id} set language: {lang}")
    # Формируем главное меню на выбранном языке
    markup = Tools.get_menu_markup(lang)
    await msg.answer(texts.get(lang, {}).get("welcome", "Welcome!"), reply_markup=markup)
    # Устанавливаем состояние главного меню
    await state.set_state(AppState.Menu)
