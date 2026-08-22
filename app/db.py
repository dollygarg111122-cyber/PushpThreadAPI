from collections.abc import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


logger = logging.getLogger("app.database")


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url, pool_pre_ping=True, fast_executemany=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        db.connection()
        yield db
    except SQLAlchemyError:
        settings = get_settings()
        logger.exception(
            "Database connection failed: server=%s port=%s database=%s driver=%s "
            "trusted_connection=%s user=%s",
            settings.db_server,
            settings.db_port,
            settings.db_name,
            settings.db_driver,
            settings.db_trusted_connection,
            settings.db_user or "<not configured>",
        )
        raise
    finally:
        db.close()
