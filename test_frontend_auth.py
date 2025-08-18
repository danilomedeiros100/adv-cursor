#!/usr/bin/env python3
"""
Script para simular o comportamento do frontend
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def simulate_frontend_flow():
    """Simula o fluxo do frontend"""
    print("🖥️ Simulando fluxo do frontend...")
    
    # 1. Login
    print("\n1. Fazendo login...")
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
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.text}")
            return
        
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login bem-sucedido! Token: {token[:50]}...")
        
        # 2. Simular busca de clientes (como o frontend faria)
        print("\n2. Testando busca de clientes...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/company/clients/?search=cl&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Busca de clientes funcionando!")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Erro na busca: {response.text}")
        
        # 3. Simular busca de usuários
        print("\n3. Testando busca de usuários...")
        response = requests.get(
            f"{BASE_URL}/company/users/?search=jo&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Busca de usuários funcionando!")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Erro na busca: {response.text}")
        
        # 4. Simular busca de especialidades
        print("\n4. Testando busca de especialidades...")
        response = requests.get(
            f"{BASE_URL}/company/specialties/?search=dir&limit=10",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Busca de especialidades funcionando!")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Erro na busca: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    simulate_frontend_flow()
