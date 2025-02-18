from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from db import async_session
from models import Cupping
from tools import Tools
from bot_dictionary import texts, parameter_names
from loguru import logger
from FSMachines import AppState

cupping_history_router = Router()

@cupping_history_router.message(lambda msg: msg.text in [
    texts["EN"]["menu_history"], texts["RU"]["menu_history"], texts["UA"]["menu_history"]
])
async def show_history(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    async with async_session() as session:
        result = await session.execute(
            "SELECT id, brewing_method, avg FROM cuppings WHERE telegram_user_id = :tid ORDER BY id DESC",
            {"tid": msg.from_user.id}
        )
        items = result.all()
    markup = Tools.get_history_markup(items, lang)
    await msg.answer(texts[lang].get("history_title", "Cupping History:"), reply_markup=markup)
    # Устанавливаем состояние истории
    await state.set_state(AppState.History)

@cupping_history_router.callback_query(lambda c: c.data.startswith("history_"))
async def history_detail(callback: CallbackQuery, state: FSMContext):
    # Извлекаем идентификатор каппинга (формат: "history_<id>")
    cid = int(callback.data.split("_")[1])
    data = await state.get_data()
    lang = data.get("language", "EN")
    async with async_session() as session:
        result = await session.execute(
            "SELECT * FROM cuppings WHERE id = :cid", {"cid": cid}
        )
        record = result.first()
    if not record:
        await callback.answer("Record not found", show_alert=True)
        return

    cupping = record[0]
    params_text = "\n".join([
        f"{parameter_names[lang][p]}: {getattr(cupping, p)}"
        for p in ['fragrance', 'aroma', 'flavor', 'aftertaste', 'acidity', 'sweetness', 'mouthfeel', 'overall']
    ])
    final_text = texts[lang]["final_summary"].format(
        id=cupping.id,
        dt=cupping.dt.strftime("%Y-%m-%d %H:%M"),
        params=params_text,
        avg=cupping.avg,
        method=cupping.brewing_method,
        bean=cupping.bean_name,
        note=cupping.note
    )

    inline_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text=texts[lang]["menu"], callback_data="to_menu"),
            types.InlineKeyboardButton(text=texts[lang]["history_button"], callback_data="to_history")
        ]
    ])
    await callback.message.edit_text(final_text, reply_markup=inline_kb)
    await callback.answer()

@cupping_history_router.callback_query(lambda c: c.data in ["to_menu", "to_history"])
async def history_nav(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    if callback.data == "to_menu":
        # Вернёмся в главное меню и установим состояние AppState.Menu
        await callback.message.edit_text(texts[lang]["welcome"], reply_markup=Tools.get_menu_markup(lang))
        await state.set_state(AppState.Menu)
    else:
        # Повторный вызов истории
        fake_msg = Message(**callback.message.to_python())
        await show_history(fake_msg, state)
    await callback.answer()
