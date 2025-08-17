#!/usr/bin/env python3
"""
Script para verificar permissões do usuário
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from core.database import SessionLocal
from core.models.tenant_user import TenantUser

def check_permissions():
    """Verifica permissões do usuário"""
    db = SessionLocal()
    
    try:
        print("🔍 Verificando permissões...")
        
        # Buscar tenant_user com role admin
        tenant_user = db.query(TenantUser).filter(TenantUser.role == 'admin').first()
        
        if not tenant_user:
            print("❌ Nenhum tenant_user com role admin encontrado")
            return
        
        print(f"   Role: {tenant_user.role}")
        print(f"   Permissões: {tenant_user.permissions}")
        
        # Verificar se tem clients.manage
        has_clients_manage = tenant_user.permissions.get('clients.manage', False)
        print(f"   Tem clients.manage: {has_clients_manage}")
        
        # Verificar se tem clients.read
        has_clients_read = tenant_user.permissions.get('clients.read', False)
        print(f"   Tem clients.read: {has_clients_read}")
        
        # Verificar se tem clients.create
        has_clients_create = tenant_user.permissions.get('clients.create', False)
        print(f"   Tem clients.create: {has_clients_create}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_permissions()
