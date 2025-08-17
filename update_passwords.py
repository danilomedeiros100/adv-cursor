#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.superadmin import SuperAdmin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_passwords():
    """Atualiza as senhas para bcrypt"""
    print("=== ATUALIZANDO SENHAS PARA BCRYPT ===")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        print("✅ Conexão com banco estabelecida")
        
        # Atualizar senha do Super Admin
        super_admin = db.query(SuperAdmin).filter(SuperAdmin.email == "admin@saasjuridico.com").first()
        if super_admin:
            super_admin.password_hash = pwd_context.hash("admin123")
            print("✅ Senha do Super Admin atualizada")
        
        # Atualizar senha do usuário João
        user_joao = db.query(User).filter(User.email == "joao@escritoriodemo.com").first()
        if user_joao:
            user_joao.password_hash = pwd_context.hash("123456")
            print("✅ Senha do João atualizada")
        
        # Atualizar senha do usuário Maria
        user_maria = db.query(User).filter(User.email == "maria@escritoriodemo.com").first()
        if user_maria:
            user_maria.password_hash = pwd_context.hash("123456")
            print("✅ Senha da Maria atualizada")
        
        # Commit das alterações
        db.commit()
        print("✅ Alterações salvas no banco")
        
        db.close()
        print("✅ Atualização concluída com sucesso")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_passwords()
