from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from core.config import settings

# Configuração do banco de dados
DATABASE_URL = settings.DATABASE_URL

# Criar engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log das queries SQL (remover em produção)
    pool_pre_ping=True,
    pool_recycle=300,
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Dependency para injeção de dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
