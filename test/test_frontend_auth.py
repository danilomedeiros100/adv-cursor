#!/usr/bin/env python3
import requests
import json

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_frontend_auth():
    """Testa autenticação via frontend"""
    print("=== TESTE DE AUTENTICAÇÃO VIA FRONTEND ===")
    
    # 1. Fazer login via backend para obter token
    print("\n1. Fazendo login via backend...")
    login_data = {
        "email": "joao@escritoriodemo.com",
        "password": "123456",
        "tenant_slug": "demo"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login bem-sucedido")
            print(f"Token obtido: {token[:50]}...")
            
            # 2. Testar criação de especialidade via frontend
            print("\n2. Testando criação de especialidade via frontend...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            specialty_data = {
                "name": "Direito Ambiental",
                "description": "Especialidade em direito ambiental"
            }
            
            response = requests.post(
                f"{FRONTEND_URL}/api/v1/company/specialties",
                headers=headers,
                json=specialty_data
            )
            
            print(f"Status da resposta: {response.status_code}")
            print(f"Resposta: {response.text}")
            
            if response.status_code == 201:
                print("✅ Especialidade criada com sucesso via frontend!")
            else:
                print("❌ Erro ao criar especialidade via frontend")
                
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_frontend_auth()
