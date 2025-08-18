#!/usr/bin/env python3
"""
Script simples para testar login
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Testa o endpoint de login com credenciais corretas"""
    print("🔐 Testando login...")
    
    # Credenciais do seed data
    login_data = {
        "email": "joao@escritoriodemo.com",
        "password": "123456",
        "tenant_slug": "demo"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        print(f"Status: {response.status_code}")
        
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

def test_clients(token):
    """Testa endpoint de clientes"""
    print("\n🔍 Testando clientes...")
    
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
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Clientes funcionando!")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    token = test_login()
    if token:
        test_clients(token)
