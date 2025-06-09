from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings


engine = create_engine(settings.DATABASE_URL)

Sessionmaker = sessionmaker(bind=engine)

Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = Sessionmaker()
    try:
        yield db
    finally:
        db.close()
