#!/usr/bin/env python3
"""
Teste das funcionalidades de CRUD de usuários no frontend
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:3000"
API_BASE = f"{BASE_URL}/api/v1/company/users"

def test_users_crud():
    """Testa as funcionalidades de CRUD de usuários"""
    
    print("🧪 Testando CRUD de Usuários no Frontend")
    print("=" * 50)
    
    # Teste 1: Listar usuários
    print("\n1. 📋 Testando listagem de usuários...")
    try:
        response = requests.get(API_BASE)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Sucesso! {len(users)} usuários encontrados")
            for user in users:
                print(f"   - {user['name']} ({user['email']}) - {user['role']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Criar usuário
    print("\n2. ➕ Testando criação de usuário...")
    new_user = {
        "name": "Teste Usuário",
        "email": "teste@exemplo.com",
        "password": "123456",
        "role": "assistant",
        "department": "Teste",
        "position": "Assistente de Teste",
        "phone": "(11) 99999-9999"
    }
    
    try:
        response = requests.post(API_BASE, json=new_user)
        if response.status_code == 201:
            created_user = response.json()
            print(f"✅ Usuário criado com sucesso! ID: {created_user['id']}")
            user_id = created_user['id']
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return
    
    # Teste 3: Visualizar usuário
    print("\n3. 👁️ Testando visualização de usuário...")
    try:
        response = requests.get(f"{API_BASE}?id={user_id}")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Usuário encontrado: {user['name']} ({user['email']})")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Atualizar usuário
    print("\n4. ✏️ Testando atualização de usuário...")
    update_data = {
        "id": user_id,
        "name": "Teste Usuário Atualizado",
        "position": "Assistente Sênior",
        "phone": "(11) 88888-8888"
    }
    
    try:
        response = requests.put(f"{API_BASE}", json=update_data)
        if response.status_code == 200:
            updated_user = response.json()
            print(f"✅ Usuário atualizado: {updated_user['name']} - {updated_user['position']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 5: Excluir usuário
    print("\n5. 🗑️ Testando exclusão de usuário...")
    try:
        response = requests.delete(f"{API_BASE}?id={user_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Usuário excluído: {result['message']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 6: Verificar se usuário foi excluído
    print("\n6. 🔍 Verificando se usuário foi excluído...")
    try:
        response = requests.get(f"{API_BASE}?id={user_id}")
        if response.status_code == 404:
            print("✅ Usuário não encontrado (excluído corretamente)")
        else:
            print(f"⚠️ Usuário ainda existe: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Teste concluído!")

def test_stats():
    """Testa as estatísticas de usuários"""
    print("\n📊 Testando estatísticas de usuários...")
    
    try:
        response = requests.get(f"{API_BASE}/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas carregadas:")
            print(f"   - Total: {stats.get('total_users', 0)}")
            print(f"   - Ativos: {stats.get('active_users', 0)}")
            print(f"   - Inativos: {stats.get('inactive_users', 0)}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_departments():
    """Testa a listagem de departamentos"""
    print("\n🏢 Testando listagem de departamentos...")
    
    try:
        response = requests.get(f"{API_BASE}/departments/list")
        if response.status_code == 200:
            data = response.json()
            departments = data.get('departments', [])
            print(f"✅ {len(departments)} departamentos encontrados:")
            for dept in departments:
                print(f"   - {dept.get('name', 'N/A')}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Executar testes
    test_users_crud()
    test_stats()
    test_departments()
