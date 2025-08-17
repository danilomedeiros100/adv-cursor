#!/usr/bin/env python3
"""
Script de teste para o CRUD de usuários
Testa criação, listagem, atualização e remoção de usuários
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
COMPANY_TOKEN = None
SUPERADMIN_TOKEN = None

def login_superadmin():
    """Login como superadmin para criar tenant"""
    global SUPERADMIN_TOKEN
    
    login_data = {
        "email": "superadmin@saas.com",
        "password": "superadmin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/superadmin/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        SUPERADMIN_TOKEN = data["access_token"]
        print("✅ Login superadmin realizado com sucesso")
        return True
    else:
        print(f"❌ Erro no login superadmin: {response.status_code} - {response.text}")
        return False

def create_tenant():
    """Cria um tenant de teste"""
    headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    
    tenant_data = {
        "name": "Escritório Teste CRUD",
        "subdomain": "teste-crud",
        "owner_email": "admin@teste.com",
        "owner_name": "Admin Teste",
        "owner_password": "admin123",
        "plan": "basic",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/superadmin/tenants", json=tenant_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Tenant criado: {data['name']} (ID: {data['id']})")
        return data
    else:
        print(f"❌ Erro ao criar tenant: {response.status_code} - {response.text}")
        return None

def login_company_admin():
    """Login como admin da empresa"""
    global COMPANY_TOKEN
    
    login_data = {
        "email": "admin@teste.com",
        "password": "admin123",
        "tenant_subdomain": "teste-crud"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        COMPANY_TOKEN = data["access_token"]
        print("✅ Login admin empresa realizado com sucesso")
        return True
    else:
        print(f"❌ Erro no login admin empresa: {response.status_code} - {response.text}")
        return False

def test_create_users():
    """Testa criação de usuários com diferentes roles"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    users_to_create = [
        {
            "name": "João Silva",
            "email": "joao.silva@teste.com",
            "password": "senha123",
            "phone": "(11) 99999-9999",
            "cpf": "123.456.789-00",
            "oab_number": "123456",
            "oab_state": "SP",
            "position": "Advogado Sênior",
            "department": "Direito Civil",
            "role": "lawyer",
            "is_active": True
        },
        {
            "name": "Maria Santos",
            "email": "maria.santos@teste.com",
            "password": "senha123",
            "phone": "(11) 88888-8888",
            "cpf": "987.654.321-00",
            "position": "Assistente Jurídico",
            "department": "Direito Civil",
            "role": "assistant",
            "is_active": True
        },
        {
            "name": "Pedro Costa",
            "email": "pedro.costa@teste.com",
            "password": "senha123",
            "phone": "(11) 77777-7777",
            "cpf": "111.222.333-44",
            "position": "Secretário",
            "department": "Administrativo",
            "role": "secretary",
            "is_active": True
        },
        {
            "name": "Ana Oliveira",
            "email": "ana.oliveira@teste.com",
            "password": "senha123",
            "phone": "(11) 66666-6666",
            "cpf": "555.666.777-88",
            "position": "Recepcionista",
            "department": "Recepção",
            "role": "receptionist",
            "is_active": True
        }
    ]
    
    created_users = []
    
    for i, user_data in enumerate(users_to_create, 1):
        print(f"\n📝 Criando usuário {i}: {user_data['name']}")
        
        response = requests.post(f"{BASE_URL}/api/v1/company/users", json=user_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            created_users.append(data)
            print(f"✅ Usuário criado: {data['name']} (ID: {data['id']})")
        else:
            print(f"❌ Erro ao criar usuário: {response.status_code} - {response.text}")
    
    return created_users

def test_list_users():
    """Testa listagem de usuários"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print("\n📋 Testando listagem de usuários...")
    
    # Lista todos os usuários
    response = requests.get(f"{BASE_URL}/api/v1/company/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Listagem: {len(users)} usuários encontrados")
        
        for user in users:
            print(f"  - {user['name']} ({user['email']}) - Role: {user.get('role', 'N/A')}")
    else:
        print(f"❌ Erro na listagem: {response.status_code} - {response.text}")
    
    # Testa filtros
    print("\n🔍 Testando filtros...")
    
    # Filtro por role
    response = requests.get(f"{BASE_URL}/api/v1/company/users?role=lawyer", headers=headers)
    if response.status_code == 200:
        lawyers = response.json()
        print(f"✅ Advogados: {len(lawyers)} encontrados")
    
    # Filtro por departamento
    response = requests.get(f"{BASE_URL}/api/v1/company/users?department=Direito Civil", headers=headers)
    if response.status_code == 200:
        civil_dept = response.json()
        print(f"✅ Departamento Civil: {len(civil_dept)} encontrados")
    
    # Filtro por busca
    response = requests.get(f"{BASE_URL}/api/v1/company/users?search=João", headers=headers)
    if response.status_code == 200:
        search_results = response.json()
        print(f"✅ Busca por 'João': {len(search_results)} encontrados")

def test_get_user(user_id):
    """Testa obtenção de usuário específico"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n👤 Obtendo usuário {user_id}...")
    
    response = requests.get(f"{BASE_URL}/api/v1/company/users/{user_id}", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Usuário obtido: {user['name']}")
        print(f"  - Email: {user['email']}")
        print(f"  - Role: {user.get('role', 'N/A')}")
        print(f"  - Departamento: {user.get('department', 'N/A')}")
        print(f"  - OAB: {user.get('oab_number', 'N/A')}")
        return user
    else:
        print(f"❌ Erro ao obter usuário: {response.status_code} - {response.text}")
        return None

def test_update_user(user_id):
    """Testa atualização de usuário"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n✏️ Atualizando usuário {user_id}...")
    
    update_data = {
        "name": "João Silva Atualizado",
        "phone": "(11) 99999-0000",
        "position": "Advogado Pleno",
        "department": "Direito Trabalhista"
    }
    
    response = requests.put(f"{BASE_URL}/api/v1/company/users/{user_id}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Usuário atualizado: {user['name']}")
        print(f"  - Novo telefone: {user['phone']}")
        print(f"  - Nova posição: {user['position']}")
        print(f"  - Novo departamento: {user['department']}")
        return user
    else:
        print(f"❌ Erro ao atualizar usuário: {response.status_code} - {response.text}")
        return None

def test_update_user_role(user_id):
    """Testa atualização de role do usuário"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n🔄 Atualizando role do usuário {user_id}...")
    
    # Atualiza para admin
    response = requests.put(f"{BASE_URL}/api/v1/company/users/{user_id}/role?role=admin", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Role atualizado para admin")
        return data
    else:
        print(f"❌ Erro ao atualizar role: {response.status_code} - {response.text}")
        return None

def test_user_stats():
    """Testa estatísticas de usuários"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print("\n📊 Obtendo estatísticas de usuários...")
    
    response = requests.get(f"{BASE_URL}/api/v1/company/users/stats/summary", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Estatísticas obtidas:")
        print(f"  - Total de usuários: {stats['total_users']}")
        print(f"  - Usuários ativos: {stats['active_users']}")
        print(f"  - Usuários inativos: {stats['inactive_users']}")
        print(f"  - Contagem por role: {stats['role_counts']}")
        print(f"  - Advogados com OAB: {stats['lawyers_with_oab']}")
        return stats
    else:
        print(f"❌ Erro ao obter estatísticas: {response.status_code} - {response.text}")
        return None

def test_departments():
    """Testa lista de departamentos"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print("\n🏢 Obtendo lista de departamentos...")
    
    response = requests.get(f"{BASE_URL}/api/v1/company/users/departments/list", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        departments = data['departments']
        print(f"✅ Departamentos encontrados: {len(departments)}")
        for dept in departments:
            print(f"  - {dept}")
        return departments
    else:
        print(f"❌ Erro ao obter departamentos: {response.status_code} - {response.text}")
        return None

def test_deactivate_user(user_id):
    """Testa desativação de usuário"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n🚫 Desativando usuário {user_id}...")
    
    response = requests.delete(f"{BASE_URL}/api/v1/company/users/{user_id}", headers=headers)
    
    if response.status_code == 200:
        print("✅ Usuário desativado com sucesso")
        return True
    else:
        print(f"❌ Erro ao desativar usuário: {response.status_code} - {response.text}")
        return False

def test_activate_user(user_id):
    """Testa reativação de usuário"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n✅ Reativando usuário {user_id}...")
    
    response = requests.post(f"{BASE_URL}/api/v1/company/users/{user_id}/activate", headers=headers)
    
    if response.status_code == 200:
        print("✅ Usuário reativado com sucesso")
        return True
    else:
        print(f"❌ Erro ao reativar usuário: {response.status_code} - {response.text}")
        return False

def test_change_password(user_id):
    """Testa alteração de senha"""
    headers = {"Authorization": f"Bearer {COMPANY_TOKEN}"}
    
    print(f"\n🔐 Testando alteração de senha para usuário {user_id}...")
    
    password_data = {
        "current_password": "senha123",
        "new_password": "nova_senha456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/company/users/{user_id}/change-password", json=password_data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Senha alterada com sucesso")
        return True
    else:
        print(f"❌ Erro ao alterar senha: {response.status_code} - {response.text}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 INICIANDO TESTES DO CRUD DE USUÁRIOS")
    print("=" * 50)
    
    # 1. Login como superadmin
    if not login_superadmin():
        return
    
    # 2. Criar tenant de teste
    tenant = create_tenant()
    if not tenant:
        return
    
    # Aguarda um pouco para o tenant ser criado
    time.sleep(2)
    
    # 3. Login como admin da empresa
    if not login_company_admin():
        return
    
    # 4. Testar criação de usuários
    created_users = test_create_users()
    if not created_users:
        print("❌ Nenhum usuário foi criado. Abortando testes.")
        return
    
    # 5. Testar listagem
    test_list_users()
    
    # 6. Testar obtenção de usuário específico
    first_user = created_users[0]
    user_details = test_get_user(first_user['id'])
    
    # 7. Testar atualização
    if user_details:
        updated_user = test_update_user(first_user['id'])
    
    # 8. Testar atualização de role
    if user_details:
        test_update_user_role(first_user['id'])
    
    # 9. Testar estatísticas
    test_user_stats()
    
    # 10. Testar departamentos
    test_departments()
    
    # 11. Testar desativação
    if len(created_users) > 1:
        test_deactivate_user(created_users[1]['id'])
        
        # Verificar se foi desativado
        time.sleep(1)
        test_list_users()
        
        # 12. Testar reativação
        test_activate_user(created_users[1]['id'])
    
    # 13. Testar alteração de senha
    if user_details:
        test_change_password(first_user['id'])
    
    print("\n" + "=" * 50)
    print("✅ TESTES DO CRUD DE USUÁRIOS CONCLUÍDOS!")
    print("=" * 50)

if __name__ == "__main__":
    main()
