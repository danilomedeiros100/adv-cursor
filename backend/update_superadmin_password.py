#!/usr/bin/env python3

from core.database import SessionLocal
from core.models.superadmin import SuperAdmin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def update_superadmin_password():
    db = SessionLocal()
    
    try:
        admin = db.query(SuperAdmin).first()
        if admin:
            admin.password_hash = pwd_context.hash("admin123")
            db.commit()
            print(f"✅ Senha atualizada para o super admin: {admin.email}")
        else:
            print("❌ Super admin não encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_superadmin_password()
