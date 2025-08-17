#!/usr/bin/env python3
import sys
import os
import uuid

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Cria um usuário de teste com todas as permissões"""
    print("=== CRIANDO USUÁRIO DE TESTE ===")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        print("✅ Conexão com banco estabelecida")
        
        # Buscar o tenant demo
        tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
        if not tenant:
            print("❌ Tenant demo não encontrado")
            return
        
        print(f"✅ Tenant demo encontrado: {tenant.name}")
        
        # Verificar se o usuário já existe
        existing_user = db.query(User).filter(User.email == "teste@teste").first()
        if existing_user:
            print("⚠️ Usuário teste@teste já existe")
            user = existing_user
        else:
            # Criar usuário de teste
            print("📝 Criando usuário de teste...")
            user = User(
                id=uuid.uuid4(),
                name="Usuário Teste",
                email="teste@teste",
                password_hash=pwd_context.hash("123456"),
                phone="(11) 99999-9999",
                oab_number="999999",
                oab_state="SP",
                position="Advogado",
                department="Geral",
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
            db.add(user)
            db.commit()
            print("✅ Usuário de teste criado")
        
        # Verificar se já existe relacionamento tenant-user
        existing_tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == user.id
        ).first()
        
        if existing_tenant_user:
            print("⚠️ Relacionamento tenant-user já existe")
            # Atualizar permissões para admin
            existing_tenant_user.role = "admin"
            existing_tenant_user.permissions = {
                "users.manage": True,
                "financial.manage": True,
                "processes.view_all": True,
                "processes.create": True,
                "processes.read": True,
                "processes.update": True,
                "processes.delete": True,
                "clients.create": True,
                "clients.read": True,
                "clients.update": True,
                "clients.delete": True,
                "specialties.manage": True,
                "documents.manage": True,
                "notifications.manage": True
            }
            existing_tenant_user.is_active = True
            existing_tenant_user.is_primary_admin = True
        else:
            # Criar relacionamento tenant-user com permissões de admin
            print("📝 Criando relacionamento tenant-user...")
            tenant_user = TenantUser(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=user.id,
                role="admin",
                permissions={
                    "users.manage": True,
                    "financial.manage": True,
                    "processes.view_all": True,
                    "processes.create": True,
                    "processes.read": True,
                    "processes.update": True,
                    "processes.delete": True,
                    "clients.create": True,
                    "clients.read": True,
                    "clients.update": True,
                    "clients.delete": True,
                    "specialties.manage": True,
                    "documents.manage": True,
                    "notifications.manage": True
                },
                department="Geral",
                position="Administrador",
                is_active=True,
                is_primary_admin=True
            )
            db.add(tenant_user)
        
        db.commit()
        print("✅ Relacionamento tenant-user criado/atualizado")
        
        # Resumo
        print("\n" + "="*50)
        print("🎉 USUÁRIO DE TESTE CRIADO COM SUCESSO!")
        print("="*50)
        print(f"Email: teste@teste")
        print(f"Senha: 123456")
        print(f"Tenant: demo")
        print(f"Role: admin")
        print(f"Permissões: Todas")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()

if __name__ == "__main__":
    create_test_user()
