from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.models.client import Client
import jwt
from typing import Optional

security = HTTPBearer()

async def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Obtém o cliente atual baseado no token JWT"""
    try:
        # Decodifica o token JWT
        # Por enquanto, vamos usar uma implementação simples
        # Em produção, você deve usar uma chave secreta real
        token = credentials.credentials
        
        # Por enquanto, vamos simular um cliente válido
        # Em uma implementação real, você decodificaria o JWT e extrairia o client_id
        # payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        # client_id = payload.get("client_id")
        
        # Por enquanto, vamos buscar o primeiro cliente disponível
        client = db.query(Client).first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cliente não encontrado"
            )
        
        return {
            "client_id": str(client.id),
            "client": client
        }
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro de autenticação: {str(e)}"
        )
