#!/usr/bin/env python3
"""
Script para criar uma empresa de teste e usuário para testar o sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.models.tenant import Tenant
from core.models.user import User
from core.models.tenant_user import TenantUser
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_company():
    """Cria uma empresa de teste"""
    db = SessionLocal()
    
    try:
        print("🏢 Criando empresa de teste...")
        
        # Criar tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Escritório de Teste",
            slug="escritorio-teste",
            email="contato@escritorioteste.com.br",
            phone="(11) 99999-9999",
            plan_type="professional",
            plan_features={
                "processos_avancados": True,
                "usuarios_10": True,
                "suporte_telefone": True,
                "relatorios": True
            },
            max_users=10,
            max_processes=500,
            is_active=True,
            is_suspended=False,
            settings={
                "timezone": "America/Sao_Paulo",
                "language": "pt-BR",
                "notifications": True
            },
            branding={
                "logo_url": None,
                "primary_color": "#3B82F6",
                "company_name": "Escritório de Teste"
            },
            created_at=datetime.now()
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        print(f"✅ Empresa criada: {tenant.name} ({tenant.slug})")
        
        return tenant
        
    except Exception as e:
        print(f"❌ Erro ao criar empresa: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_test_user(tenant_id):
    """Cria um usuário de teste"""
    db = SessionLocal()
    
    try:
        print("👤 Criando usuário de teste...")
        
        # Criar usuário
        user = User(
            id=uuid.uuid4(),
            name="João Silva",
            email="joao.silva@escritorioteste.com.br",
            phone="(11) 99999-1111",
            password_hash=pwd_context.hash("123456"),
            oab_number="123456/SP",
            oab_state="SP",
            position="Advogado Sênior",
            department="Direito Civil",
            is_active=True,
            is_super_admin=False,
            email_verified=True,
            phone_verified=True,
            preferences={
                "theme": "light",
                "notifications": True,
                "language": "pt-BR"
            },
            timezone="America/Sao_Paulo",
            language="pt-BR",
            created_at=datetime.now()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Usuário criado: {user.name} ({user.email})")
        
        return user
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_tenant_user(tenant_id, user_id):
    """Associa usuário ao tenant"""
    db = SessionLocal()
    
    try:
        print("🔗 Associando usuário à empresa...")
        
        # Criar associação
        tenant_user = TenantUser(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            role="admin",
            permissions={
                "users.manage": True,
                "users.create": True,
                "users.read": True,
                "users.update": True,
                "users.delete": True,
                "clients.manage": True,
                "processes.manage": True,
                "specialties.manage": True,
                "financial.manage": True,
                "reports.view": True
            },
            is_active=True,
            is_primary_admin=True,
            created_at=datetime.now()
        )
        
        db.add(tenant_user)
        db.commit()
        db.refresh(tenant_user)
        
        print(f"✅ Usuário associado à empresa com permissões de admin")
        
        return tenant_user
        
    except Exception as e:
        print(f"❌ Erro ao associar usuário: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 Criando dados de teste para empresa...")
    print("=" * 50)
    
    # 1. Criar empresa
    tenant = create_test_company()
    if not tenant:
        print("❌ Falha ao criar empresa")
        return
    
    # 2. Criar usuário
    user = create_test_user(tenant.id)
    if not user:
        print("❌ Falha ao criar usuário")
        return
    
    # 3. Associar usuário à empresa
    tenant_user = create_tenant_user(tenant.id, user.id)
    if not tenant_user:
        print("❌ Falha ao associar usuário")
        return
    
    print("\n" + "=" * 50)
    print("✅ Dados de teste criados com sucesso!")
    print("\n📋 Credenciais de acesso:")
    print(f"   📧 Email: {user.email}")
    print(f"   🔑 Senha: 123456")
    print(f"   🏢 Empresa: {tenant.name}")
    print(f"   🔗 Slug: {tenant.slug}")
    print("\n🔗 URL de acesso:")
    print("   http://localhost:3000/auth/login")
    print("\n💡 Use estas credenciais para testar o sistema!")

if __name__ == "__main__":
    main()
