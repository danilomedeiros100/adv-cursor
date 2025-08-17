#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.tenant_user import TenantUser
from apps.auth.routes import authenticate_user

def test_auth_direct():
    """Testa autenticação diretamente"""
    print("=== TESTE DE AUTENTICAÇÃO DIRETA ===")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        print("✅ Conexão com banco estabelecida")
        
        # Testar autenticação do usuário João
        print("\n--- Testando autenticação do João ---")
        auth_result = authenticate_user(db, "joao@escritoriodemo.com", "123456", "demo")
        
        if auth_result:
            print("✅ Autenticação do João bem-sucedida")
            user = auth_result["user"]
            tenant = auth_result.get("tenant")
            print(f"  - Usuário: {user.name} ({user.email})")
            print(f"  - Tenant: {tenant.name if tenant else 'Nenhum'}")
            print(f"  - Super Admin: {auth_result.get('is_super_admin', False)}")
        else:
            print("❌ Falha na autenticação do João")
        
        # Testar autenticação do Super Admin
        print("\n--- Testando autenticação do Super Admin ---")
        auth_result = authenticate_user(db, "admin@saasjuridico.com", "admin123")
        
        if auth_result:
            print("✅ Autenticação do Super Admin bem-sucedida")
            user = auth_result["user"]
            print(f"  - Usuário: {user.name} ({user.email})")
            print(f"  - Super Admin: {auth_result.get('is_super_admin', False)}")
        else:
            print("❌ Falha na autenticação do Super Admin")
        
        # Verificar se o usuário João tem acesso ao tenant demo
        print("\n--- Verificando acesso do João ao tenant demo ---")
        tenant = db.query(Tenant).filter(Tenant.slug == "demo").first()
        if tenant:
            print(f"✅ Tenant demo encontrado: {tenant.name}")
            
            user = db.query(User).filter(User.email == "joao@escritoriodemo.com").first()
            if user:
                print(f"✅ Usuário João encontrado: {user.name}")
                
                tenant_user = db.query(TenantUser).filter(
                    TenantUser.tenant_id == tenant.id,
                    TenantUser.user_id == user.id,
                    TenantUser.is_active == True
                ).first()
                
                if tenant_user:
                    print("✅ Usuário João tem acesso ao tenant demo")
                    print(f"  - Role: {tenant_user.role}")
                    print(f"  - Ativo: {tenant_user.is_active}")
                else:
                    print("❌ Usuário João NÃO tem acesso ao tenant demo")
            else:
                print("❌ Usuário João não encontrado")
        else:
            print("❌ Tenant demo não encontrado")
        
        db.close()
        print("\n✅ Teste concluído")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_direct()
