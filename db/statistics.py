import asyncio
from sqlalchemy import text, select, func, desc
from db.database import *
from db.models import *


class AdminStatistics:

    @staticmethod
    async def get_count_of_users():
        async with async_session_factory() as session:
            count = await session.execute(select(func.count()).select_from(UsersORM))
            result = count.scalar()
        return result

    @staticmethod
    async def get_the_most_active_user():
        async with async_session_factory() as session:
            result = await session.execute(select(UsersORM).order_by(desc(UsersORM.message_count)).limit(1))
            user_id = result.scalars().first().telegram_id
        return user_id

    @staticmethod
    async def get_the_most_popular_value():
        async with async_session_factory() as session:
            result = await session.execute(
                select(ValuesORM.name, func.count(ValuesORM.name).label('count'))
                .group_by(ValuesORM.name)
                .order_by(desc('count'))
                .limit(1)
            )
            value_name = result.scalars().first()
        return value_name


