#!/usr/bin/env python3
"""
Script para atualizar permissões do usuário admin
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from core.database import SessionLocal
from core.models.tenant_user import TenantUser

def update_permissions():
    """Atualiza permissões do usuário admin"""
    db = SessionLocal()
    
    try:
        print("🔧 Atualizando permissões...")
        
        # Buscar tenant_user com role admin
        tenant_user = db.query(TenantUser).filter(TenantUser.role == 'admin').first()
        
        if not tenant_user:
            print("❌ Nenhum tenant_user com role admin encontrado")
            return
        
        print(f"   Usuário: {tenant_user.user_id}")
        print(f"   Tenant: {tenant_user.tenant_id}")
        print(f"   Role: {tenant_user.role}")
        print(f"   Permissões atuais: {tenant_user.permissions}")
        
        # Atualizar permissões para incluir clients
        current_permissions = tenant_user.permissions or {}
        updated_permissions = {
            **current_permissions,
            'clients.manage': True,
            'clients.read': True,
            'clients.create': True,
            'clients.update': True,
            'clients.delete': True
        }
        
        tenant_user.permissions = updated_permissions
        db.commit()
        
        print(f"   Permissões atualizadas: {tenant_user.permissions}")
        print("✅ Permissões atualizadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_permissions()
