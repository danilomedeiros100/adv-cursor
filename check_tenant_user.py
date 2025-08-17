#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser

def check_tenant_user():
    """Verifica o relacionamento tenant-user"""
    print("=== VERIFICANDO RELACIONAMENTO TENANT-USER ===")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        print("✅ Conexão com banco estabelecida")
        
        # Buscar o tenant demo
        tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
        if not tenant:
            print("❌ Tenant demo não encontrado")
            return
        
        print(f"✅ Tenant demo encontrado: {tenant.name} (ID: {tenant.id})")
        
        # Buscar o usuário João
        user = db.query(User).filter(User.email == "joao@escritoriodemo.com").first()
        if not user:
            print("❌ Usuário João não encontrado")
            return
        
        print(f"✅ Usuário João encontrado: {user.name} (ID: {user.id})")
        
        # Verificar relacionamento tenant-user
        tenant_user = db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant.id,
            TenantUser.user_id == user.id
        ).first()
        
        if tenant_user:
            print("✅ Relacionamento tenant-user encontrado:")
            print(f"  - ID: {tenant_user.id}")
            print(f"  - Role: {tenant_user.role}")
            print(f"  - Ativo: {tenant_user.is_active}")
            print(f"  - Admin Principal: {tenant_user.is_primary_admin}")
            print(f"  - Permissões: {tenant_user.permissions}")
        else:
            print("❌ Relacionamento tenant-user NÃO encontrado")
            
            # Listar todos os relacionamentos do tenant
            all_tenant_users = db.query(TenantUser).filter(TenantUser.tenant_id == tenant.id).all()
            print(f"📋 Relacionamentos existentes no tenant demo: {len(all_tenant_users)}")
            for tu in all_tenant_users:
                user_info = db.query(User).filter(User.id == tu.user_id).first()
                print(f"  - {user_info.name if user_info else 'Usuário não encontrado'} ({tu.user_id}) - Role: {tu.role} - Ativo: {tu.is_active}")
        
        # Listar todos os relacionamentos do usuário
        user_tenants = db.query(TenantUser).filter(TenantUser.user_id == user.id).all()
        print(f"📋 Tenants do usuário João: {len(user_tenants)}")
        for ut in user_tenants:
            tenant_info = db.query(Tenant).filter(Tenant.id == ut.tenant_id).first()
            print(f"  - {tenant_info.name if tenant_info else 'Tenant não encontrado'} ({ut.tenant_id}) - Role: {ut.role} - Ativo: {ut.is_active}")
        
        db.close()
        print("\n✅ Verificação concluída")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_tenant_user()
