import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy import URL, create_engine, text
from config.config_reader import config


DATABASE_URL_ASYNC = f'postgresql+asyncpg://{config.DB_USER}:' \
                     f'{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'

async_engine = create_async_engine(
    url=DATABASE_URL_ASYNC,
    echo=False
)

async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass


class DatabaseCreator:
    @staticmethod
    async def create_table_users():
        query = """
        CREATE TABLE IF NOT EXISTS users (
        telegram_id BIGINT PRIMARY KEY,
        message_count INT,
        voice TEXT
        );
        """
        async with async_engine.begin() as conn:
            await conn.execute(text(query))

    @staticmethod
    async def create_table_values():
        query = """
        CREATE TABLE IF NOT EXISTS user_values (
        id SERIAL PRIMARY KEY,
        name TEXT,
        rating INT,
        telegram_id BIGINT,
        FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
        );
        """
        async with async_engine.begin() as conn:
            await conn.execute(text(query))


