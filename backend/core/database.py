import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

Base = declarative_base()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency FastAPI que fornece uma sessao SQLAlchemy por request."""
    db: Session = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        logging.error(f"Erro na conexao com o DB: {exc}")
        raise exc
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager para codigo fora do sistema de dependencies do FastAPI."""
    db: Session = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as exc:
        logging.error(f"Erro na conexao com o DB: {exc}")
        raise exc
    finally:
        db.close()


def get_db_session():
    """Alias mantido para endpoints existentes de autenticacao."""
    yield from get_db()


def create_all_tables():
    Base.metadata.create_all(bind=engine)
    logging.info("Todas as tabelas foram criadas ou ja existiam.")
