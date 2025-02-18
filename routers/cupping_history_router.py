# routers/cupping_history_router.py
from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from db import async_session
from models import Cupping
from tools import Tools
from bot_dictionary import texts, parameter_names
from loguru import logger
import datetime

cupping_history_router = Router()

@cupping_history_router.message(lambda msg: msg.text in [texts["EN"]["menu_history"], texts["RU"]["menu_history"], texts["UA"]["menu_history"]])
async def show_history(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    async with async_session() as session:
        result = await session.execute(
            "SELECT id, brewing_method, avg FROM cuppings WHERE telegram_user_id = :tid",
            {"tid": msg.from_user.id}
        )
        items = result.all()
    markup = Tools.get_history_markup(items, lang)
    await msg.answer("History:", reply_markup=markup)

@cupping_history_router.callback_query(lambda c: c.data.startswith("history_"))
async def history_detail(callback: CallbackQuery, state: FSMContext):
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
        f"{parameter_names[lang][p]}: {getattr(cupping, p)}" for p, _, _ in [
            ("fragrance", None, None),
            ("aroma", None, None),
            ("flavor", None, None),
            ("aftertaste", None, None),
            ("acidity", None, None),
            ("sweetness", None, None),
            ("mouthfeel", None, None),
            ("overall", None, None),
        ]
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
    markup = Tools.get_menu_markup(lang)
    btn_hist = types.InlineKeyboardButton(text=texts[lang]["history_button"], callback_data="to_history")
    inline_kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text=texts[lang]["menu"], callback_data="to_menu"),
        btn_hist
    )
    await callback.message.edit_text(final_text, reply_markup=inline_kb)
    await callback.answer()

@cupping_history_router.callback_query(lambda c: c.data in ["to_menu", "to_history"])
async def history_nav(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "EN")
    if callback.data == "to_menu":
        await callback.message.edit_text(texts[lang]["welcome"], reply_markup=Tools.get_menu_markup(lang))
    else:
        from aiogram.types import Message
        fake_msg = Message(**callback.message.to_python())
        await show_history(fake_msg, state)
    await callback.answer()
