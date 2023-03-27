from sqlalchemy import Column, String, Integer, ForeignKey, BIGINT
from sqlalchemy.orm import relationship, mapped_column
from .base import Base
from .base_model import BaseModel
from .database import async_db_session
from sqlalchemy.future import select


class UserCharacter(Base, BaseModel):
    __tablename__ = "user_character"
    # Create table fields
    character = Column(String, nullable=False, primary_key=True)
    elo = Column(Integer, nullable=False, default=800)
    user_id = mapped_column(
        BIGINT, ForeignKey("user.id"), primary_key=True, nullable=False
    )
    user = relationship("User", back_populates="character_history")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    async def get_from_user_and_character(user_id: str, character: str):
        query = select(UserCharacter).where(
            (UserCharacter.user_id == user_id) & (UserCharacter.character == character)
        )
        results = await async_db_session.execute(query)
        result = results.first()
        if result is None:
            return await UserCharacter.create(character=character, user_id=user_id)
        return result[0]

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user={self.user.in_game_name}, "
            f"character={self.character}, "
            f"elo={self.elo}, "
            f")>"
        )
