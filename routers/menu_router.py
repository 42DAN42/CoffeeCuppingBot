# routers/menu_router.py
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from tools import Tools
from bot_dictionary import texts
from loguru import logger
from FSMachines import CuppingState, CandidateState

menu_router = Router()

@menu_router.message()
async def menu_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()
    if text == texts[lang]["menu_start_cupping"]:
        logger.info(f"User {msg.from_user.id} chose to start cupping.")
        await state.set_state(CuppingState.RatingFragrance)
        param_text = texts[lang]["rate_parameter"].format(param=__import__("bot_dictionary").parameter_names[lang]["fragrance"])
        markup = Tools.get_rating_keyboard(lang)
        await msg.answer(param_text, reply_markup=markup)
    elif text == texts[lang]["menu_history"]:
        logger.info(f"User {msg.from_user.id} requested cupping history.")
        from routers import cupping_history_router  # For handling history actions.
        await msg.answer("Loading history...", reply_markup=Tools.get_history_markup([], lang))
    elif text == texts[lang]["menu_change_language"]:
        logger.info(f"User {msg.from_user.id} requested language change.")
        markup = Tools.get_language_markup()
        await msg.answer(texts[lang]["choose_language"], reply_markup=markup)
        await state.set_state(CandidateState.SelectLanguage)
