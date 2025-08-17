import asyncio
from sqlalchemy import text
from core.database import engine, Base
from core.models import *

async def test_db():
    print("Testando conexão com banco de dados...")
    
    try:
        # Testar conexão síncrona
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Conexão OK:", result.fetchone())
            
            # Testar criação de tabelas
            print("Criando tabelas...")
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas com sucesso!")
            
    except Exception as e:
        print("Erro na conexão:", e)

if __name__ == "__main__":
    asyncio.run(test_db())
