from sqlalchemy import Table, Integer, String, MetaData, Column, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base


class UsersORM(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_count: Mapped[int] = mapped_column(nullable=True)
    voice: Mapped[str]


class ValuesORM(Base):
    __tablename__ = 'user_values'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rating: Mapped[int]
    telegram_id: Mapped[int] = mapped_column(BigInteger,
                                             ForeignKey(UsersORM.telegram_id, ondelete='CASCADE'))




