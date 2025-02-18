import datetime
from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from FSMachines import CuppingState
from bot_dictionary import texts, parameter_names
from tools import Tools
from loguru import logger
from db import async_session
from models import Cupping

cupping_router = Router()

# Последовательность параметров оценки и переходов состояний.
PARAMS_SEQUENCE = [
    ("fragrance", CuppingState.RatingFragrance, CuppingState.RatingAroma),
    ("aroma", CuppingState.RatingAroma, CuppingState.RatingFlavor),
    ("flavor", CuppingState.RatingFlavor, CuppingState.RatingAftertaste),
    ("aftertaste", CuppingState.RatingAftertaste, CuppingState.RatingAcidity),
    ("acidity", CuppingState.RatingAcidity, CuppingState.RatingSweetness),
    ("sweetness", CuppingState.RatingSweetness, CuppingState.RatingMouthfeel),
    ("mouthfeel", CuppingState.RatingMouthfeel, CuppingState.RatingOverall),
    ("overall", CuppingState.RatingOverall, CuppingState.BrewingMethod),
]

# Множество значений состояний (строк) для этапов оценки.
# Здесь берём именно те состояния, которые используются для ввода рейтингов.
EXPECTED_RATING_STATES = {state.state for _, state, _ in PARAMS_SEQUENCE}


def get_param_info(state_value: str, lang: str):
    """
    Возвращает (имя_параметра, следующее_состояние, отображаемое_название_параметра)
    по значению текущего состояния (строка).
    """
    for param, curr_state, next_state in PARAMS_SEQUENCE:
        if curr_state.state == state_value:
            return param, next_state, parameter_names[lang][param]
    return None, None, None


# Фильтр для этапов рейтинга.
async def is_rating_state(msg: Message, state: FSMContext) -> bool:
    current_state = await state.get_state()
    return current_state in EXPECTED_RATING_STATES


# Фабрика фильтров для проверки равенства текущего состояния с target_state.
def state_equals(target_state: str):
    async def predicate(msg: Message, state: FSMContext) -> bool:
        return (await state.get_state()) == target_state

    return predicate


# ---------- Обработчик этапов ввода рейтингов (отвечает только, если состояние – одно из EXPECTED_RATING_STATES) ----------
@cupping_router.message(is_rating_state)
async def rating_message_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()  # текущее состояние – строка
    logger.debug(f"rating_message_handler: user {msg.from_user.id} in state '{current_state}' sent: '{msg.text}'")

    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()

    # Обработка кнопки «Back»
    if text == texts[lang].get("back", "Back"):
        if current_state == CuppingState.RatingFragrance.state:
            await msg.answer(texts[lang]["menu"], reply_markup=Tools.get_menu_markup(lang))
            await state.clear()
            logger.debug(f"User {msg.from_user.id}: pressed back in first rating state. Returning to main menu.")
            return
        else:
            # Переход на предыдущий шаг
            for idx, (param, curr_state, _) in enumerate(PARAMS_SEQUENCE):
                if curr_state.state == current_state:
                    if idx > 0:
                        prev_param, prev_state, _ = PARAMS_SEQUENCE[idx - 1]
                        await state.set_state(prev_state.state)
                        prompt = texts[lang]["rate_parameter"].format(param=parameter_names[lang][prev_param])
                        await msg.answer(prompt, reply_markup=Tools.get_rating_keyboard(lang))
                        logger.debug(f"User {msg.from_user.id}: pressed back. Returning to state '{prev_state.state}'.")
                    else:
                        await msg.answer(texts[lang]["menu"], reply_markup=Tools.get_menu_markup(lang))
                        await state.clear()
                        logger.debug(f"User {msg.from_user.id}: pressed back in first state. Returning to main menu.")
                    break
        return

    # Обработка числовой оценки.
    try:
        rating = float(text)
    except ValueError:
        await msg.answer("Invalid input. Please send a number or press back.",
                         reply_markup=Tools.get_rating_keyboard(lang))
        logger.debug(f"User {msg.from_user.id}: invalid rating input '{text}' in state '{current_state}'.")
        return

    param, next_state, param_display = get_param_info(current_state, lang)
    if param is None:
        await msg.answer("Unknown state.")
        logger.debug(f"User {msg.from_user.id}: unknown state '{current_state}'.")
        return

    await state.update_data(**{param: rating})
    logger.debug(f"User {msg.from_user.id}: rated '{param}' = {rating} in state '{current_state}'.")

    # Если следующим состоянием является метод заваривания, переходим в него.
    if next_state.state == CuppingState.BrewingMethod.state:
        await state.set_state(CuppingState.BrewingMethod.state)
        prompt = texts[lang]["brewing_method"]
        await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
        logger.debug(f"User {msg.from_user.id}: moving to BrewingMethod state.")
        return
    else:
        await state.set_state(next_state.state)
        next_param_display = None
        for par, st, _ in PARAMS_SEQUENCE:
            if st.state == next_state.state:
                next_param_display = parameter_names[lang][par]
                break
        if next_param_display is None:
            next_param_display = "Unknown parameter"
        prompt = texts[lang]["rate_parameter"].format(param=next_param_display)
        await msg.answer(prompt, reply_markup=Tools.get_rating_keyboard(lang))
        logger.debug(f"User {msg.from_user.id}: moving to next rating state '{next_state.state}'.")


# ---------- Обработчик ввода метода заваривания (срабатывает, если состояние = BrewingMethod) ----------
@cupping_router.message(state_equals(CuppingState.BrewingMethod.state))
async def brewing_method_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.debug(f"brewing_method_handler: user {msg.from_user.id} in state '{current_state}' sent: '{msg.text}'")
    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()

    if text == texts[lang].get("back", "Back"):
        # Возврат к оценке параметра "overall"
        await state.set_state(CuppingState.RatingOverall.state)
        prompt = texts[lang]["rate_parameter"].format(param=parameter_names[lang]["overall"])
        await msg.answer(prompt, reply_markup=Tools.get_rating_keyboard(lang))
        logger.debug(f"User {msg.from_user.id}: pressed back in BrewingMethod state. Returning to RatingOverall state.")
        return

    await state.update_data(brewing_method=text)
    await state.set_state(CuppingState.BeanName.state)
    prompt = texts[lang]["bean_name"]
    await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
    logger.debug(f"User {msg.from_user.id}: set brewing_method='{text}'. Moving to BeanName state.")


# ---------- Обработчик ввода названия бина (срабатывает, если состояние = BeanName) ----------
@cupping_router.message(state_equals(CuppingState.BeanName.state))
async def bean_name_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.debug(f"bean_name_handler: user {msg.from_user.id} in state '{current_state}' sent: '{msg.text}'")
    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()

    if text == texts[lang].get("back", "Back"):
        await state.set_state(CuppingState.BrewingMethod.state)
        prompt = texts[lang]["brewing_method"]
        await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
        logger.debug(f"User {msg.from_user.id}: pressed back in BeanName state. Returning to BrewingMethod state.")
        return

    await state.update_data(bean_name=text)
    await state.set_state(CuppingState.Note.state)
    prompt = texts[lang]["note"]
    await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
    logger.debug(f"User {msg.from_user.id}: set bean_name='{text}'. Moving to Note state.")


# ---------- Обработчик ввода текстового замечания (срабатывает, если состояние = Note) ----------
@cupping_router.message(state_equals(CuppingState.Note.state))
async def note_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.debug(f"note_handler: user {msg.from_user.id} in state '{current_state}' sent: '{msg.text}'")
    data = await state.get_data()
    lang = data.get("language", "EN")
    text = msg.text.strip()

    if text == texts[lang].get("back", "Back"):
        await state.set_state(CuppingState.BeanName.state)
        prompt = texts[lang]["bean_name"]
        await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
        logger.debug(f"User {msg.from_user.id}: pressed back in Note state. Returning to BeanName state.")
        return

    await state.update_data(note=text)
    # Подсчитываем среднее значение по оценкам.
    ratings = []
    for param, _, _ in PARAMS_SEQUENCE:
        r = data.get(param)
        if r is not None:
            ratings.append(r)
    average = sum(ratings) / len(ratings) if ratings else 0
    await state.update_data(avg=average)

    # Создаём объект для записи в БД.
    cupping = Cupping(
        telegram_user_id=msg.from_user.id,
        fragrance=data.get("fragrance"),
        aroma=data.get("aroma"),
        flavor=data.get("flavor"),
        aftertaste=data.get("aftertaste"),
        acidity=data.get("acidity"),
        sweetness=data.get("sweetness"),
        mouthfeel=data.get("mouthfeel"),
        overall=data.get("overall"),
        brewing_method=data.get("brewing_method"),
        bean_name=data.get("bean_name"),
        note=text,
        avg=average
    )

    # Используем асинхронный контекстный менеджер для работы с сессией.
    try:
        async with async_session() as session:
            session.add(cupping)
            await session.commit()
            await session.refresh(cupping)
            cupping_id = cupping.id
    except Exception as err:
        logger.error(f"Error during session commit for user {msg.from_user.id}: {err}")
        raise

    params_text = "\n".join([f"{parameter_names[lang][p]}: {data.get(p)}" for p, _, _ in PARAMS_SEQUENCE])
    final_text = texts[lang]["final_summary"].format(
        id=cupping_id,
        dt=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        params=params_text,
        avg=average,
        method=data.get("brewing_method"),
        bean=data.get("bean_name"),
        note=text
    )
    await msg.answer(final_text, reply_markup=Tools.get_menu_markup(lang))
    logger.debug(f"User {msg.from_user.id}: finished cupping. Final data: {data} and note: '{text}'")
    await state.clear()
