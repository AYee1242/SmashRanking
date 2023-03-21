from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, mapped_column
from .base import Base
from .base_model import BaseModel
import enum


class Character(Base, BaseModel):
    __tablename__ = "character"
    # Create table fields
    character = Column(String, nullable=False, primary_key=True)
    elo = Column(Integer, nullable=False)
    user_id = mapped_column(
        String(20), ForeignKey("user.id"), primary_key=True, nullable=False
    )
    user = relationship("User", back_populates="character_elos")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"user={self.user.in_game_name}, "
            f"character={self.character}, "
            f"elo={self.elo}, "
            f"wins={self.wins}"
            f"loses={self.losses}"
            f")>"
        )
