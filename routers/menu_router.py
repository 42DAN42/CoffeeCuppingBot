from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from tools import Tools
from bot_dictionary import texts, parameter_names
from loguru import logger
from FSMachines import CuppingState, CandidateState, AppState

menu_router = Router()

@menu_router.message(lambda message: message.text in [
    texts["EN"]["menu_start_cupping"], texts["RU"]["menu_start_cupping"], texts["UA"]["menu_start_cupping"],
    texts["EN"]["menu_history"], texts["RU"]["menu_history"], texts["UA"]["menu_history"],
    texts["EN"]["menu_change_language"], texts["RU"]["menu_change_language"], texts["UA"]["menu_change_language"]
])
async def menu_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()

    if text == texts[lang]["menu_start_cupping"]:
        logger.info(f"User {msg.from_user.id} chose to start cupping.")
        # Переходим в цепочку оценки кофе – первое состояние: RatingFragrance
        await state.set_state(CuppingState.RatingFragrance)
        param_text = texts[lang]["rate_parameter"].format(param=parameter_names[lang]["fragrance"])
        markup = Tools.get_rating_keyboard(lang)
        await msg.answer(param_text, reply_markup=markup)

    elif text == texts[lang]["menu_history"]:
        logger.info(f"User {msg.from_user.id} requested cupping history.")
        # Устанавливаем состояние истории
        await state.set_state(AppState.History)
        await msg.answer(texts[lang].get("loading_history", "Loading history..."),
                         reply_markup=Tools.get_history_markup([], lang))

    elif text == texts[lang]["menu_change_language"]:
        logger.info(f"User {msg.from_user.id} requested language change.")
        markup = Tools.get_language_markup()
        await msg.answer(texts[lang]["choose_language"], reply_markup=markup)
        # Возвращаемся к состоянию выбора языка
        await state.set_state(CandidateState.SelectLanguage)
