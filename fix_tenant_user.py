#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser
import uuid

def fix_tenant_user():
    """Corrige o relacionamento tenant-user"""
    print("=== CORRIGINDO RELACIONAMENTO TENANT-USER ===")
    
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
        
        # Buscar o usuário João
        user_joao = db.query(User).filter(User.email == "joao@escritoriodemo.com").first()
        if not user_joao:
            print("❌ Usuário João não encontrado")
            return
        
        print(f"✅ Usuário João encontrado: {user_joao.name}")
        
        # Buscar o usuário Maria
        user_maria = db.query(User).filter(User.email == "maria@escritoriodemo.com").first()
        if not user_maria:
            print("❌ Usuário Maria não encontrado")
            return
        
        print(f"✅ Usuário Maria encontrado: {user_maria.name}")
        
        # Verificar se já existe relacionamento
        existing_joao = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == user_joao.id
        ).first()
        
        if existing_joao:
            print("✅ Relacionamento do João já existe")
        else:
            # Criar relacionamento para o João
            tenant_user_joao = TenantUser(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=user_joao.id,
                role="admin",
                permissions={
                    "users.manage": True,
                    "financial.manage": True,
                    "processes.view_all": True,
                    "specialties.manage": True
                },
                department="Administrativo",
                position="Sócio",
                is_active=True,
                is_primary_admin=True
            )
            db.add(tenant_user_joao)
            print("✅ Relacionamento do João criado")
        
        # Verificar se já existe relacionamento para Maria
        existing_maria = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == user_maria.id
        ).first()
        
        if existing_maria:
            print("✅ Relacionamento da Maria já existe")
        else:
            # Criar relacionamento para a Maria
            tenant_user_maria = TenantUser(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=user_maria.id,
                role="lawyer",
                permissions={
                    "processes.create": True,
                    "processes.read": True,
                    "processes.update": True,
                    "clients.create": True,
                    "clients.read": True,
                    "clients.update": True
                },
                department="Civil",
                position="Advogada",
                is_active=True,
                is_primary_admin=False
            )
            db.add(tenant_user_maria)
            print("✅ Relacionamento da Maria criado")
        
        # Commit das alterações
        db.commit()
        print("✅ Alterações salvas no banco")
        
        # Verificar se funcionou
        print("\n--- Verificando relacionamentos criados ---")
        tenant_users = db.query(TenantUser).filter(TenantUser.tenant_id == tenant.id).all()
        print(f"📋 Relacionamentos no tenant demo: {len(tenant_users)}")
        for tu in tenant_users:
            user_info = db.query(User).filter(User.id == tu.user_id).first()
            print(f"  - {user_info.name} - Role: {tu.role} - Ativo: {tu.is_active}")
        
        db.close()
        print("\n✅ Correção concluída com sucesso")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_tenant_user()
