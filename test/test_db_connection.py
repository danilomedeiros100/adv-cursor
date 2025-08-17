#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_db
from core.models.user import User
from core.models.tenant import Tenant
from core.models.superadmin import SuperAdmin

def test_db_connection():
    """Testa a conexão com o banco de dados"""
    print("=== TESTE DE CONEXÃO COM BANCO DE DADOS ===")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        print("✅ Conexão com banco estabelecida")
        
        # Testar consulta de usuários
        users = db.query(User).all()
        print(f"✅ Usuários encontrados: {len(users)}")
        
        # Testar consulta de tenants
        tenants = db.query(Tenant).all()
        print(f"✅ Tenants encontrados: {len(tenants)}")
        
        # Testar consulta de super admins
        super_admins = db.query(SuperAdmin).all()
        print(f"✅ Super Admins encontrados: {len(super_admins)}")
        
        # Mostrar detalhes dos usuários
        for user in users:
            print(f"  - {user.name} ({user.email}) - Ativo: {user.is_active}")
        
        # Mostrar detalhes dos tenants
        for tenant in tenants:
            print(f"  - {tenant.name} ({tenant.slug}) - Ativo: {tenant.is_active}")
        
        # Mostrar detalhes dos super admins
        for admin in super_admins:
            print(f"  - {admin.name} ({admin.email}) - Ativo: {admin.is_active}")
        
        db.close()
        print("✅ Teste concluído com sucesso")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_connection()
