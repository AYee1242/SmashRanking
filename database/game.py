from sqlalchemy import Column, String, Integer, ForeignKey, DATE
from sqlalchemy.orm import relationship, mapped_column
from .base import Base
from .base_model import BaseModel


class Game(Base, BaseModel):
    __tablename__ = "game"
    # Create table fields
    id = Column(Integer, primary_key=True)
    date = Column(DATE, nullable=False)
    user_games = relationship("UserGame", back_populates="game")

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(" f"id={self.id}, " f"date={self.date}" f")>"
        )
