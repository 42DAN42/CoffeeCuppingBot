# routers/start_router.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from FSMachines import CandidateState
from tools import Tools
from bot_dictionary import texts
from loguru import logger

start_router = Router()

@start_router.message(Command("start"))
async def start_handler(msg: Message, state):
    await state.clear()
    logger.info(f"User {msg.from_user.id} started the bot.")
    markup = Tools.get_language_markup()
    await msg.answer(texts["EN"]["choose_language"], reply_markup=markup)
    await state.set_state(CandidateState.SelectLanguage)
