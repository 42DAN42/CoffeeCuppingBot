import datetime
from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from FSMachines import CuppingState
from bot_dictionary import texts, parameter_names
from tools import Tools
from loguru import logger
from sqlalchemy import select
from db import async_session
from models import Cupping

cupping_router = Router()

# Определяем порядок параметров и состояний.
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


def get_param_info(state_name: str, lang: str):
    for param, curr_state, next_state in PARAMS_SEQUENCE:
        if curr_state == state_name:
            return param, next_state, parameter_names[lang][param]
    return None, None, None


@cupping_router.callback_query(lambda c: c.data.isdigit() or c.data == "back")
async def rating_callback_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    current_state = await state.get_state()
    cb_data = callback.data

    # Обработка кнопки "Back"
    if cb_data == "back":
        if current_state == CuppingState.RatingFragrance.state:
            await callback.message.answer(texts[lang]["menu"], reply_markup=Tools.get_menu_markup(lang))
            await state.clear()
            await callback.answer()
            return
        else:
            for idx, (param, curr_state, _) in enumerate(PARAMS_SEQUENCE):
                if curr_state == current_state:
                    if idx > 0:
                        prev_param, _, _ = PARAMS_SEQUENCE[idx - 1]
                        prev_state = PARAMS_SEQUENCE[idx - 1][1]
                        await state.set_state(prev_state)
                        prompt = texts[lang]["rate_parameter"].format(param=parameter_names[lang][prev_param])
                        await callback.message.edit_text(prompt, reply_markup=Tools.get_rating_keyboard(lang))
                    else:
                        await callback.message.answer(texts[lang]["menu"], reply_markup=Tools.get_menu_markup(lang))
                        await state.clear()
                    break
        await callback.answer()
        return

    try:
        rating = float(cb_data)
    except ValueError:
        await callback.answer("Invalid data", show_alert=True)
        return

    param, next_state, param_display = get_param_info(current_state, lang)
    if param is None:
        await callback.answer("Unknown state.")
        return

    await state.update_data(**{param: rating})
    logger.info(f"User {callback.from_user.id} rated {param} = {rating}")

    if next_state == CuppingState.BrewingMethod:
        await state.set_state(CuppingState.BrewingMethod)
        prompt = texts[lang]["brewing_method"]
        await callback.message.edit_text(prompt, reply_markup=Tools.get_note_back_markup(lang))
        await callback.answer()
        return
    else:
        await state.set_state(next_state)
        next_param_display = None
        for par, st, _ in PARAMS_SEQUENCE:
            if st == next_state:
                next_param_display = parameter_names[lang][par]
                break
        if next_param_display is None:
            next_param_display = "Unknown parameter"
        prompt = texts[lang]["rate_parameter"].format(param=next_param_display)
        await callback.message.edit_text(prompt, reply_markup=Tools.get_rating_keyboard(lang))
        await callback.answer()


@cupping_router.message(CuppingState.Note)
async def note_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    if msg.text == texts[lang]["back"]:
        await state.set_state(CuppingState.BeanName)
        prompt = texts[lang]["bean_name"]
        await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
        return
    await state.update_data(note=msg.text)
    ratings = []
    for param, _, _ in PARAMS_SEQUENCE:
        ratings.append(data.get(param))
    if data.get("overall") is not None:
        ratings[-1] = data.get("overall")
    average = sum(ratings) / len(ratings)
    await state.update_data(avg=average)
    async with async_session() as session:
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
            note=msg.text,
            avg=average
        )
        session.add(cupping)
        await session.commit()
        await session.refresh(cupping)
        cupping_id = cupping.id
    params_text = "\n".join([
        f"{parameter_names[lang][p]}: {data.get(p)}" for p, _, _ in PARAMS_SEQUENCE
    ])
    final_text = texts[lang]["final_summary"].format(
        id=cupping_id,
        dt=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        params=params_text,
        avg=average,
        method=data.get("brewing_method"),
        bean=data.get("bean_name"),
        note=msg.text
    )
    await msg.answer(final_text, reply_markup=Tools.get_menu_markup(lang))
    await state.clear()


@cupping_router.message(CuppingState.BrewingMethod)
async def brewing_method_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    if msg.text == texts[lang]["back"]:
        await state.set_state(CuppingState.RatingOverall)
        prompt = texts[lang]["rate_parameter"].format(param=parameter_names[lang]["overall"])
        await msg.answer(prompt, reply_markup=Tools.get_rating_keyboard(lang))
        return
    await state.update_data(brewing_method=msg.text)
    await state.set_state(CuppingState.BeanName)
    prompt = texts[lang]["bean_name"]
    await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))


@cupping_router.message(CuppingState.BeanName)
async def bean_name_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    if msg.text == texts[lang]["back"]:
        await state.set_state(CuppingState.BrewingMethod)
        prompt = texts[lang]["brewing_method"]
        await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
        return
    await state.update_data(bean_name=msg.text)
    await state.set_state(CuppingState.Note)
    prompt = texts[lang]["note"]
    await msg.answer(prompt, reply_markup=Tools.get_note_back_markup(lang))
