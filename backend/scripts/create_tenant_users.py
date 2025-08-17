#!/usr/bin/env python3
"""
Script para criar associações TenantUser
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.models import Tenant, User, TenantUser
import uuid

def create_tenant_users():
    """Criar associações TenantUser"""
    db = SessionLocal()
    
    try:
        print("🔗 Criando associações usuário-tenant...")
        
        # Buscar tenant demo
        demo_tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
        if not demo_tenant:
            print("❌ Tenant 'demo' não encontrado!")
            return
        
        # Buscar usuários
        admin_user = db.query(User).filter(User.email == "joao@escritoriodemo.com").first()
        lawyer_user = db.query(User).filter(User.email == "maria@escritoriodemo.com").first()
        
        if not admin_user:
            print("❌ Usuário admin não encontrado!")
            return
        
        if not lawyer_user:
            print("❌ Usuário advogada não encontrado!")
            return
        
        # Verificar se já existem associações
        existing_admin = db.query(TenantUser).filter(
            TenantUser.tenant_id == demo_tenant.id,
            TenantUser.user_id == admin_user.id
        ).first()
        
        existing_lawyer = db.query(TenantUser).filter(
            TenantUser.tenant_id == demo_tenant.id,
            TenantUser.user_id == lawyer_user.id
        ).first()
        
        if existing_admin and existing_lawyer:
            print("✅ Associações já existem!")
            return
        
        # Criar associação do admin com o tenant
        if not existing_admin:
            print("1. Criando associação admin-tenant...")
            admin_tenant_user = TenantUser(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                user_id=admin_user.id,
                role="admin",
                permissions={
                    "users.manage": True,
                    "users.read": True,
                    "users.create": True,
                    "users.update": True,
                    "users.delete": True,
                    "clients.manage": True,
                    "clients.read": True,
                    "clients.create": True,
                    "clients.update": True,
                    "clients.delete": True,
                    "processes.manage": True,
                    "processes.read": True,
                    "processes.create": True,
                    "processes.update": True,
                    "processes.delete": True,
                    "specialties.manage": True,
                    "specialties.read": True,
                    "specialties.create": True,
                    "specialties.update": True,
                    "specialties.delete": True,
                    "documents.manage": True,
                    "documents.read": True,
                    "documents.create": True,
                    "documents.update": True,
                    "documents.delete": True,
                    "financial.manage": True,
                    "financial.read": True,
                    "financial.create": True,
                    "financial.update": True,
                    "financial.delete": True,
                    "reports.manage": True,
                    "reports.read": True,
                    "settings.manage": True,
                    "settings.read": True,
                    "admin": True
                },
                is_active=True
            )
            db.add(admin_tenant_user)
        
        # Criar associação da advogada com o tenant
        if not existing_lawyer:
            print("2. Criando associação advogada-tenant...")
            lawyer_tenant_user = TenantUser(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                user_id=lawyer_user.id,
                role="lawyer",
                permissions={
                    "users.read": True,
                    "clients.manage": True,
                    "clients.read": True,
                    "clients.create": True,
                    "clients.update": True,
                    "processes.manage": True,
                    "processes.read": True,
                    "processes.create": True,
                    "processes.update": True,
                    "specialties.read": True,
                    "documents.manage": True,
                    "documents.read": True,
                    "documents.create": True,
                    "documents.update": True,
                    "financial.read": True,
                    "reports.read": True,
                    "settings.read": True
                },
                is_active=True
            )
            db.add(lawyer_tenant_user)
        
        # Commit das alterações
        db.commit()
        
        print("✅ Associações criadas com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("=" * 50)
        print("🏢 Empresa Demo - Admin:")
        print("   Email: joao@escritoriodemo.com")
        print("   Senha: 123456")
        print("   Tenant: demo")
        print()
        print("👩‍💼 Empresa Demo - Advogada:")
        print("   Email: maria@escritoriodemo.com")
        print("   Senha: 123456")
        print("   Tenant: demo")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar associações: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_tenant_users()
