from .database import async_db_session
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.future import select


class BaseModel:
    @classmethod
    async def create(
        cls,
        **kwargs,
    ):
        async_db_session.add(cls(**kwargs))
        try:
            await async_db_session.commit()
        except Exception as e:
            await async_db_session.rollback()
            raise e

    @classmethod
    async def update(cls, id, **kwargs):
        query = (
            sqlalchemy_update(cls)
            .where(cls.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        try:
            await async_db_session.execute(query)
            await async_db_session.commit()
        except Exception as e:
            await async_db_session.rollback()
            raise e

    @classmethod
    async def get(cls, id):
        query = select(cls).where(cls.id == id)
        results = await async_db_session.execute(query)
        result = results.first()
        if result is None:
            return result
        return result[0]

    @classmethod
    async def exists(cls, id):
        query = select(cls).where(cls.id == id)
        results = await async_db_session.execute(query)
        return result
