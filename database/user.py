from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base
from .base_model import BaseModel
from sqlalchemy.future import select
from .database import async_db_session


class User(Base, BaseModel):
    __tablename__ = "user"
    # Create table fields
    id = Column(String(20), primary_key=True)
    in_game_name = Column(String(250), nullable=False, unique=True)
    elo = Column(Integer, nullable=False, default=800)
    current_character = Column(String, nullable=True)
    user_game_history = relationship("UserGame", back_populates="user")
    character_history = relationship("UserCharacter", back_populates="user")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"in_game_name={self.in_game_name}, "
            f"elo={self.elo}"
            f")>"
        )

    async def get_from_name(in_game_name: str):
        query = select(User).where(User.in_game_name == in_game_name)
        results = await async_db_session.execute(query)
        result = results.first()
        if result is None:
            return result
        return result[0]
