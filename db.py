import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///cupping.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Используем обобщенный тип для sessionmaker, чтобы указать тип сессии
async_session = sessionmaker[AsyncSession](
    bind=engine,
    expire_on_commit=False,
    future=True
)


async def init_db():
    # Импортируем модели и создаём таблицы.
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
