from sqlalchemy import Column, String, Integer
from .base import Base
from .base_model import BaseModel


class Users(Base, BaseModel):
    __tablename__ = "users"
    # Create table fields
    id = Column(String(20), primary_key=True)
    in_game_name = Column(String(250), nullable=False)
    elo = Column(Integer, nullable=False, default=800)

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"in_game_name={self.in_game_name}, "
            f"elo={self.elo}, "
            f")>"
        )
