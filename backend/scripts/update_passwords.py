#!/usr/bin/env python3
"""
Script para atualizar senhas com bcrypt
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from core.database import SessionLocal
from core.models.user import User
from core.models.superadmin import SuperAdmin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_passwords():
    """Atualizar senhas para bcrypt"""
    db = SessionLocal()
    
    try:
        print("🔐 Atualizando senhas...")
        
        # Atualizar Super Admin
        super_admin = db.query(SuperAdmin).filter(SuperAdmin.email == "admin@saasjuridico.com").first()
        if super_admin:
            super_admin.password_hash = pwd_context.hash("admin123")
            print("✅ Senha do Super Admin atualizada")
        
        # Atualizar usuários
        users = [
            ("joao@escritoriodemo.com", "123456"),
            ("maria@escritoriodemo.com", "123456")
        ]
        
        for email, password in users:
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.password_hash = pwd_context.hash(password)
                print(f"✅ Senha do usuário {email} atualizada")
        
        db.commit()
        print("✅ Todas as senhas foram atualizadas com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar senhas: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_passwords()
