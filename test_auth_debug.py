#!/usr/bin/env python3
"""
Script para testar autenticação e debug do problema 401
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def test_login():
    """Testa o endpoint de login"""
    print("🔐 Testando endpoint de login...")
    
    # Dados de teste - ajuste conforme necessário
    login_data = {
        "email": "admin@empresa.com",
        "password": "admin123",
        "tenant_slug": "empresa-teste"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
            return data.get('access_token')
        else:
            print(f"❌ Erro no login: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_clients_endpoint(token):
    """Testa o endpoint de clientes com token"""
    print("\n🔍 Testando endpoint de clientes...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/company/clients/?search=cl&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de clientes funcionando!")
            print(f"Total de clientes: {data.get('total', 0)}")
            return True
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_users_endpoint(token):
    """Testa o endpoint de usuários com token"""
    print("\n👥 Testando endpoint de usuários...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/company/users/?search=ad&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de usuários funcionando!")
            print(f"Total de usuários: {data.get('total', 0)}")
            return True
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_specialties_endpoint(token):
    """Testa o endpoint de especialidades com token"""
    print("\n⚖️ Testando endpoint de especialidades...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/company/specialties/?search=dir&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de especialidades funcionando!")
            print(f"Total de especialidades: {data.get('total', 0)}")
            return True
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes de autenticação...")
    
    # Testa login
    token = test_login()
    
    if not token:
        print("\n❌ Não foi possível obter token. Verifique:")
        print("1. Se o servidor está rodando na porta 8000")
        print("2. Se as credenciais estão corretas")
        print("3. Se o tenant existe no banco de dados")
        return
    
    # Testa endpoints com token
    test_clients_endpoint(token)
    test_users_endpoint(token)
    test_specialties_endpoint(token)
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
