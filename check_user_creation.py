#!/usr/bin/env python3
"""
Script para verificar se o usuário owner foi criado corretamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from core.database import SessionLocal
from core.models.user import User
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser

def check_user_creation():
    """Verifica se o usuário owner foi criado corretamente"""
    db = SessionLocal()
    
    try:
        print("🔍 Verificando criação de usuários...")
        
        # Verificar usuários criados
        users = db.query(User).all()
        print(f"\n📊 Total de usuários: {len(users)}")
        
        for user in users:
            print(f"   - {user.name} ({user.email}) - Ativo: {user.is_active}")
            if user.password_hash:
                print(f"     Senha: {'✅ Definida' if len(user.password_hash) > 10 else '❌ Vazia'}")
            else:
                print(f"     Senha: ❌ NÃO DEFINIDA")
        
        # Verificar tenants
        tenants = db.query(Tenant).all()
        print(f"\n🏢 Total de tenants: {len(tenants)}")
        
        for tenant in tenants:
            print(f"   - {tenant.name} ({tenant.slug}) - Ativo: {tenant.is_active}")
        
        # Verificar relacionamentos tenant-user
        tenant_users = db.query(TenantUser).all()
        print(f"\n🔗 Total de relacionamentos tenant-user: {len(tenant_users)}")
        
        for tu in tenant_users:
            user = db.query(User).filter(User.id == tu.user_id).first()
            tenant = db.query(Tenant).filter(Tenant.id == tu.tenant_id).first()
            print(f"   - {user.name if user else 'N/A'} em {tenant.name if tenant else 'N/A'} - Role: {tu.role} - Admin: {tu.is_primary_admin}")
        
        # Verificar usuários mais recentes
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        print(f"\n🆕 Usuários mais recentes:")
        
        for user in recent_users:
            print(f"   - {user.name} ({user.email}) - Criado: {user.created_at}")
            if user.password_hash:
                print(f"     Senha: ✅ Definida ({len(user.password_hash)} chars)")
            else:
                print(f"     Senha: ❌ NÃO DEFINIDA")
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user_creation()
