from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, mapped_column
from .base import Base
from .base_model import BaseModel
import enum


class GameResult(enum.Enum):
    winner = 1
    loser = 2


class UserGame(Base, BaseModel):
    __tablename__ = "user_game"
    # Create table fields
    id = Column(Integer, primary_key=True)
    game_result = Column(Enum(GameResult), nullable=False)
    elo_change = Column(Integer, nullable=False)
    character = Column(String, nullable=False)
    user_id = mapped_column(String(20), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="user_game_history")
    game_id = mapped_column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("Game", back_populates="user_games")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"game_result={self.game_result.name}, "
            f"elo_change={self.elo_change}, "
            f"user_id={self.user_id}, "
            f"game_id={self.game_id}"
            f")>"
        )
