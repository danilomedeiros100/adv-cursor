#!/usr/bin/env python3
"""
Script minimalista para criar dados essenciais da Fase 1
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import SessionLocal, engine
from werkzeug.security import generate_password_hash
import uuid

def create_seed_data():
    """Criar dados essenciais para Fase 1"""
    db = SessionLocal()
    
    try:
        print("🌱 Criando dados essenciais para Fase 1...")
        
        # 1. Criar Super Admin diretamente no banco
        print("1. Criando Super Admin...")
        super_admin_data = {
            "id": str(uuid.uuid4()),
            "name": "Super Administrador",
            "email": "admin@saasjuridico.com",
            "password_hash": generate_password_hash("admin123"),
            "is_active": True
        }
        
        # Inserir Super Admin
        db.execute(text("""
            INSERT INTO super_admins (id, name, email, password_hash, is_active, created_at)
            VALUES (:id, :name, :email, :password_hash, :is_active, NOW())
            ON CONFLICT (email) DO NOTHING
        """), super_admin_data)
        
        # 2. Criar Tenant demo
        print("2. Criando Tenant demo...")
        tenant_data = {
            "id": str(uuid.uuid4()),
            "name": "Escritório Demo",
            "slug": "demo",
            "email": "contato@escritoriodemo.com",
            "phone": "(11) 99999-9999",
            "plan_type": "premium",
            "plan_features": '{"max_users": 50, "max_processes": 1000, "modules": ["clients", "processes", "documents", "financial", "notifications"]}',
            "max_users": 50,
            "max_processes": 1000,
            "is_active": True,
            "is_suspended": False,
            "settings": '{"timezone": "America/Sao_Paulo", "language": "pt_BR", "currency": "BRL"}',
            "branding": '{"logo_url": null, "primary_color": "#3B82F6", "company_name": "Escritório Demo"}'
        }
        
        # Inserir Tenant
        db.execute(text("""
            INSERT INTO tenants (id, name, slug, email, phone, plan_type, plan_features, max_users, max_processes, is_active, is_suspended, settings, branding, created_at)
            VALUES (:id, :name, :slug, :email, :phone, :plan_type, :plan_features, :max_users, :max_processes, :is_active, :is_suspended, :settings, :branding, NOW())
            ON CONFLICT (slug) DO NOTHING
        """), tenant_data)
        
        # 3. Criar usuário admin da empresa
        print("3. Criando usuário admin da empresa...")
        admin_user_data = {
            "id": str(uuid.uuid4()),
            "name": "João Silva",
            "email": "joao@escritoriodemo.com",
            "password_hash": generate_password_hash("123456"),
            "phone": "(11) 88888-8888",
            "oab_number": "123456",
            "oab_state": "SP",
            "position": "Sócio",
            "department": "Administrativo",
            "is_active": True,
            "is_super_admin": False,
            "email_verified": True,
            "phone_verified": True,
            "preferences": '{"theme": "light", "notifications": {"email": true, "push": true, "sms": false}}',
            "timezone": "America/Sao_Paulo",
            "language": "pt_BR"
        }
        
        # Inserir usuário admin
        db.execute(text("""
            INSERT INTO users (id, name, email, password_hash, phone, oab_number, oab_state, position, department, is_active, is_super_admin, email_verified, phone_verified, preferences, timezone, language, created_at)
            VALUES (:id, :name, :email, :password_hash, :phone, :oab_number, :oab_state, :position, :department, :is_active, :is_super_admin, :email_verified, :phone_verified, :preferences, :timezone, :language, NOW())
            ON CONFLICT (email) DO NOTHING
        """), admin_user_data)
        
        # 4. Criar relacionamento tenant-user
        print("4. Criando relacionamento tenant-user...")
        tenant_user_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_data["id"],
            "user_id": admin_user_data["id"],
            "role": "admin",
            "permissions": '{"users.manage": true, "processes.manage": true, "clients.manage": true, "financial.manage": true}',
            "department": "Administrativo",
            "position": "Sócio",
            "is_active": True,
            "is_primary_admin": True
        }
        
        # Inserir relacionamento
        db.execute(text("""
            INSERT INTO tenant_users (id, tenant_id, user_id, role, permissions, department, position, is_active, is_primary_admin, created_at)
            VALUES (:id, :tenant_id, :user_id, :role, :permissions, :department, :position, :is_active, :is_primary_admin, NOW())
            ON CONFLICT (tenant_id, user_id) DO NOTHING
        """), tenant_user_data)
        
        # Commit das alterações
        db.commit()
        
        print("✅ Dados criados com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("Super Admin:")
        print("  Email: admin@saasjuridico.com")
        print("  Senha: admin123")
        print("\nEmpresa Demo:")
        print("  Email: joao@escritoriodemo.com")
        print("  Senha: 123456")
        print("  Tenant: demo")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
