#!/usr/bin/env python3
"""
Script para criar dados de teste para o Super Admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.models.superadmin import SuperAdmin
from core.models.tenant import Tenant
from core.models.user import User
from core.models.tenant_user import TenantUser
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_super_admin():
    """Cria um super admin de teste"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe super admin
        existing_admin = db.query(SuperAdmin).first()
        if existing_admin:
            print("Super Admin já existe!")
            return existing_admin
        
        # Criar super admin
        super_admin = SuperAdmin(
            id=uuid.uuid4(),
            name="Administrador do Sistema",
            email="admin@sistema.com",
            password_hash=pwd_context.hash("admin123"),
            is_active=True,
            permissions={
                "manage_tenants": True,
                "manage_users": True,
                "view_analytics": True,
                "system_config": True,
                "backup_restore": True,
                "security_audit": True
            }
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print(f"✅ Super Admin criado com sucesso!")
        print(f"   Email: {super_admin.email}")
        print(f"   Senha: admin123")
        print(f"   ID: {super_admin.id}")
        
        return super_admin
        
    except Exception as e:
        print(f"❌ Erro ao criar Super Admin: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_test_tenants():
    """Cria tenants de teste"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem tenants
        existing_tenants = db.query(Tenant).count()
        if existing_tenants > 0:
            print(f"Já existem {existing_tenants} tenants no sistema!")
            return
        
        # Dados de empresas de teste
        test_tenants = [
            {
                "name": "Escritório Silva & Associados",
                "slug": "silva-associados",
                "email": "contato@silvaassociados.com.br",
                "phone": "(11) 99999-9999",
                "plan_type": "professional",
                "max_users": 10,
                "max_processes": 500
            },
            {
                "name": "Advocacia Santos Ltda",
                "slug": "advocacia-santos",
                "email": "admin@advocaciasantos.com.br",
                "phone": "(21) 88888-8888",
                "plan_type": "enterprise",
                "max_users": 25,
                "max_processes": 1000
            },
            {
                "name": "Sociedade de Advogados Costa",
                "slug": "costa-advocacia",
                "email": "geral@costaadvocacia.com.br",
                "phone": "(31) 77777-7777",
                "plan_type": "basic",
                "max_users": 5,
                "max_processes": 200
            },
            {
                "name": "Escritório Ferreira & Oliveira",
                "slug": "ferreira-oliveira",
                "email": "contato@ferreiraoliveira.com.br",
                "phone": "(41) 66666-6666",
                "plan_type": "premium",
                "max_users": 50,
                "max_processes": 2000
            },
            {
                "name": "Advocacia Moderna",
                "slug": "advocacia-moderna",
                "email": "admin@advocaciamoderna.com.br",
                "phone": "(51) 55555-5555",
                "plan_type": "professional",
                "max_users": 15,
                "max_processes": 750
            }
        ]
        
        created_tenants = []
        for tenant_data in test_tenants:
            tenant = Tenant(
                id=uuid.uuid4(),
                name=tenant_data["name"],
                slug=tenant_data["slug"],
                email=tenant_data["email"],
                phone=tenant_data["phone"],
                plan_type=tenant_data["plan_type"],
                plan_features={
                    "basic": ["processos_basicos", "usuarios_5", "suporte_email"],
                    "professional": ["processos_avancados", "usuarios_10", "suporte_telefone", "relatorios"],
                    "enterprise": ["processos_ilimitados", "usuarios_25", "suporte_24h", "relatorios_avancados", "api"],
                    "premium": ["tudo_enterprise", "usuarios_50", "consultoria", "personalizacao"]
                },
                max_users=tenant_data["max_users"],
                max_processes=tenant_data["max_processes"],
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
                    "company_name": tenant_data["name"]
                },
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
            )
            
            db.add(tenant)
            created_tenants.append(tenant)
        
        db.commit()
        
        print(f"✅ {len(created_tenants)} tenants criados com sucesso!")
        for tenant in created_tenants:
            print(f"   - {tenant.name} ({tenant.slug})")
        
        return created_tenants
        
    except Exception as e:
        print(f"❌ Erro ao criar tenants: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def create_test_users():
    """Cria usuários de teste"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem usuários
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Já existem {existing_users} usuários no sistema!")
            return
        
        # Dados de usuários de teste
        test_users = [
            {
                "name": "João Silva",
                "email": "joao.silva@silvaassociados.com.br",
                "phone": "(11) 99999-1111",
                "oab_number": "123456/SP",
                "oab_state": "SP",
                "position": "Advogado Sênior",
                "department": "Direito Civil"
            },
            {
                "name": "Maria Santos",
                "email": "maria.santos@advocaciasantos.com.br",
                "phone": "(21) 88888-2222",
                "oab_number": "654321/RJ",
                "oab_state": "RJ",
                "position": "Sócia",
                "department": "Direito Trabalhista"
            },
            {
                "name": "Pedro Costa",
                "email": "pedro.costa@costaadvocacia.com.br",
                "phone": "(31) 77777-3333",
                "oab_number": "789012/MG",
                "oab_state": "MG",
                "position": "Advogado",
                "department": "Direito Empresarial"
            },
            {
                "name": "Ana Ferreira",
                "email": "ana.ferreira@ferreiraoliveira.com.br",
                "phone": "(41) 66666-4444",
                "oab_number": "345678/PR",
                "oab_state": "PR",
                "position": "Advogada Sênior",
                "department": "Direito Tributário"
            },
            {
                "name": "Carlos Oliveira",
                "email": "carlos.oliveira@advocaciamoderna.com.br",
                "phone": "(51) 55555-5555",
                "oab_number": "901234/RS",
                "oab_state": "RS",
                "position": "Sócio",
                "department": "Direito Digital"
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user = User(
                id=uuid.uuid4(),
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                password_hash=pwd_context.hash("senha123"),
                oab_number=user_data["oab_number"],
                oab_state=user_data["oab_state"],
                position=user_data["position"],
                department=user_data["department"],
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
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
            )
            
            db.add(user)
            created_users.append(user)
        
        db.commit()
        
        print(f"✅ {len(created_users)} usuários criados com sucesso!")
        for user in created_users:
            print(f"   - {user.name} ({user.email})")
        
        return created_users
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def create_tenant_users():
    """Associa usuários aos tenants"""
    db = SessionLocal()
    
    try:
        # Verificar se já existem associações
        existing_tenant_users = db.query(TenantUser).count()
        if existing_tenant_users > 0:
            print(f"Já existem {existing_tenant_users} associações de usuários!")
            return
        
        # Buscar tenants e usuários
        tenants = db.query(Tenant).all()
        users = db.query(User).all()
        
        if not tenants or not users:
            print("❌ Não há tenants ou usuários para associar!")
            return
        
        # Criar associações
        tenant_user_roles = [
            {"role": "admin", "permissions": {"manage_users": True, "manage_processes": True, "view_reports": True}},
            {"role": "advogado", "permissions": {"manage_processes": True, "view_reports": True}},
            {"role": "assistente", "permissions": {"view_processes": True}},
            {"role": "estagiario", "permissions": {"view_processes": True}}
        ]
        
        associations_created = 0
        
        for i, tenant in enumerate(tenants):
            if i < len(users):
                user = users[i]
                role_data = tenant_user_roles[i % len(tenant_user_roles)]
                
                tenant_user = TenantUser(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    user_id=user.id,
                    role=role_data["role"],
                    permissions=role_data["permissions"],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.add(tenant_user)
                associations_created += 1
        
        db.commit()
        
        print(f"✅ {associations_created} associações de usuários criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar associações: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 Criando dados de teste para Super Admin...")
    print("=" * 50)
    
    # Criar super admin
    print("\n1. Criando Super Admin...")
    super_admin = create_super_admin()
    
    # Criar tenants
    print("\n2. Criando Tenants...")
    tenants = create_test_tenants()
    
    # Criar usuários
    print("\n3. Criando Usuários...")
    users = create_test_users()
    
    # Associar usuários aos tenants
    print("\n4. Associando Usuários aos Tenants...")
    create_tenant_users()
    
    print("\n" + "=" * 50)
    print("✅ Dados de teste criados com sucesso!")
    print("\n📋 Resumo:")
    print("   - Super Admin: admin@sistema.com / admin123")
    print("   - Tenants: 5 empresas de teste")
    print("   - Usuários: 5 usuários de teste")
    print("   - Associações: Usuários vinculados aos tenants")
    print("\n🔗 URLs de acesso:")
    print("   - Super Admin: http://localhost:3000/superadmin/login")
    print("   - Empresas: http://localhost:3000/auth/login")

if __name__ == "__main__":
    main()
