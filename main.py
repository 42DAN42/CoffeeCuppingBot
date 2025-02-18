# main.py
import asyncio
from aiogram import Bot, Dispatcher
from loguru import logger
from db import init_db
from routers import start_router, lang_router, menu_router, cupping_router, cupping_history_router

from utils import parse_env

TOKEN = parse_env("token")


async def main():
    logger.add("bot.log", format="[{time}] {level} {message}", level="INFO")
    await init_db()
    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router.start_router)
    dp.include_router(lang_router.lang_router)
    dp.include_router(menu_router.menu_router)
    dp.include_router(cupping_router.cupping_router)
    dp.include_router(cupping_history_router.cupping_history_router)

    logger.info("Bot started polling")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
