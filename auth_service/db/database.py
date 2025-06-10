from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL,
    pool_size=10,
    max_overflow=0,
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
