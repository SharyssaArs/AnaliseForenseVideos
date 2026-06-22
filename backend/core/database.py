# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging

# Configura o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Base para os modelos
Base = declarative_base()

# Configuração do engine MySQL com pool de conexões
DATABASE_URL = "mysql+pymysql://app_user:app_password@localhost/forensic_db"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,  # reconexão automática
)

# Sessão configurada
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função get_db() como gerador para FastAPI
@contextmanager
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logging.error(f"Erro na conexão com o DB: {e}")
        # relança a exceção caso queira que o endpoint trate o erro
        raise e
    finally:
        db.close()


def get_db_session():
    """Fornece uma sessao SQLAlchemy para dependencies do FastAPI."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar todas as tabelas na inicialização
def create_all_tables():
    Base.metadata.create_all(bind=engine)
    logging.info("Todas as tabelas foram criadas ou já existiam.")
