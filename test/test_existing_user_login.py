#!/usr/bin/env python3
"""
Script para testar login de usuários existentes
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def test_existing_user_login():
    """Testa login de usuários existentes"""
    
    # Testar login do usuário demo
    login_data = {
        "email": "joao@escritoriodemo.com",
        "password": "123456"
    }
    
    print("🧪 Testando login de usuário existente...")
    print(f"   Email: {login_data['email']}")
    
    response = requests.post(f"{BASE_URL}/auth/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login do usuário demo realizado com sucesso!")
        print(f"   Token: {result['access_token'][:50]}...")
        tenant = result.get('tenant')
        if tenant:
            print(f"   Tenant: {tenant.get('name', 'N/A')}")
        else:
            print(f"   Tenant: Nenhum tenant associado")
        return True
    else:
        print(f"❌ Erro no login do usuário demo: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return False

def test_owner_login():
    """Testa login de um usuário owner criado recentemente"""
    
    # Usar o último usuário owner criado
    login_data = {
        "email": "maria-1755302373@escritorioteste.com",
        "password": "123456"
    }
    
    print("\n🧪 Testando login de usuário owner...")
    print(f"   Email: {login_data['email']}")
    
    response = requests.post(f"{BASE_URL}/auth/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login do owner realizado com sucesso!")
        print(f"   Token: {result['access_token'][:50]}...")
        tenant = result.get('tenant')
        if tenant:
            print(f"   Tenant: {tenant.get('name', 'N/A')}")
        else:
            print(f"   Tenant: Nenhum tenant associado")
        return True
    else:
        print(f"❌ Erro no login do owner: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return False

if __name__ == "__main__":
    test_existing_user_login()
    test_owner_login()
