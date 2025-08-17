#!/usr/bin/env python3
"""
Script simplificado para criar dados iniciais do sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.models import Tenant, User, SuperAdmin, TenantUser
from werkzeug.security import generate_password_hash
import uuid

def create_seed_data():
    """Criar dados iniciais do sistema"""
    db = SessionLocal()
    
    try:
        print("🌱 Criando dados iniciais...")
        
        # 1. Criar Super Admin
        print("1. Criando Super Admin...")
        super_admin = SuperAdmin(
            id=uuid.uuid4(),
            name="Super Administrador",
            email="admin@saasjuridico.com",
            password_hash=generate_password_hash("admin123"),
            is_active=True
        )
        db.add(super_admin)
        db.flush()
        
        # 2. Criar Tenant demo
        print("2. Criando Tenant demo...")
        demo_tenant = Tenant(
            id=uuid.uuid4(),
            name="Escritório Demo",
            slug="demo",
            email="contato@escritoriodemo.com",
            phone="(11) 99999-9999",
            plan_type="premium",
            plan_features={
                "max_users": 50,
                "max_processes": 1000,
                "modules": ["clients", "processes", "documents", "financial", "notifications"]
            },
            max_users=50,
            max_processes=1000,
            is_active=True,
            is_suspended=False,
            settings={
                "timezone": "America/Sao_Paulo",
                "language": "pt_BR",
                "currency": "BRL"
            },
            branding={
                "logo_url": None,
                "primary_color": "#3B82F6",
                "company_name": "Escritório Demo"
            }
        )
        db.add(demo_tenant)
        db.flush()
        
        # 3. Criar usuário admin da empresa
        print("3. Criando usuário admin da empresa...")
        admin_user = User(
            id=uuid.uuid4(),
            name="João Silva",
            email="joao@escritoriodemo.com",
            password_hash=generate_password_hash("123456"),
            phone="(11) 88888-8888",
            oab_number="123456",
            oab_state="SP",
            position="Sócio",
            department="Administrativo",
            is_active=True,
            is_super_admin=False,
            email_verified=True,
            phone_verified=True,
            preferences={
                "theme": "light",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            timezone="America/Sao_Paulo",
            language="pt_BR"
        )
        db.add(admin_user)
        db.flush()
        
        # 4. Criar usuário advogado
        print("4. Criando usuário advogado...")
        lawyer_user = User(
            id=uuid.uuid4(),
            name="Maria Santos",
            email="maria@escritoriodemo.com",
            password_hash=generate_password_hash("123456"),
            phone="(11) 77777-7777",
            oab_number="654321",
            oab_state="SP",
            position="Advogada",
            department="Civil",
            is_active=True,
            is_super_admin=False,
            email_verified=True,
            phone_verified=True,
            preferences={
                "theme": "light",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            timezone="America/Sao_Paulo",
            language="pt_BR"
        )
        db.add(lawyer_user)
        db.flush()
        
        # 5. Criar associações TenantUser
        print("5. Criando associações usuário-tenant...")
        
        # Associação do admin com o tenant
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
        
        # Associação da advogada com o tenant
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
        
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("=" * 50)
        print("🔐 Super Admin:")
        print("   Email: admin@saasjuridico.com")
        print("   Senha: admin123")
        print()
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
        print(f"❌ Erro ao criar dados iniciais: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
