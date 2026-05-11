from contextlib import contextmanager
from typing import TypeVar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from config.database_config import DatabaseConfig


class Base(DeclarativeBase):
    pass


T = TypeVar("T", bound=DeclarativeBase)


class Database:
    def __init__(self, database_config: DatabaseConfig = DatabaseConfig()):
        self.engine = create_engine(database_config.url_connection)
        self._Session: sessionmaker[Session] = sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        session: Session = self._Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = Database()
