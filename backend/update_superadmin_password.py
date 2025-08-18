#!/usr/bin/env python3
"""
Script para atualizar a senha do Super Admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from core.models.superadmin import SuperAdmin
from apps.auth.routes import get_password_hash

def update_superadmin_password():
    """Atualiza a senha do Super Admin"""
    db = SessionLocal()
    
    try:
        # Buscar o super admin
        super_admin = db.query(SuperAdmin).first()
        
        if not super_admin:
            print("❌ Nenhum Super Admin encontrado!")
            return
        
        # Nova senha
        new_password = "admin123"
        new_hash = get_password_hash(new_password)
        
        # Atualizar a senha
        super_admin.password_hash = new_hash
        db.commit()
        
        print(f"✅ Senha do Super Admin atualizada com sucesso!")
        print(f"📧 Email: {super_admin.email}")
        print(f"🔑 Nova senha: {new_password}")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_superadmin_password()
