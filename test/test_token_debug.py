#!/usr/bin/env python3
import requests
import json

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_auth():
    """Testa autenticação no backend"""
    print("=== TESTE DE AUTENTICAÇÃO NO BACKEND ===")
    
    # Teste de login
    login_data = {
        "email": "joao@escritoriodemo.com",
        "password": "123456",
        "tenant_slug": "demo"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/auth/login", json=login_data)
        print(f"Status do login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"Token obtido: {token[:20]}..." if token else "Token não encontrado")
            
            # Teste de criação de especialidade com token
            if token:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                specialty_data = {
                    "name": "Teste Especialidade",
                    "description": "Especialidade de teste",
                    "code": "TEST",
                    "is_active": True,
                    "requires_oab": False
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/company/specialties",
                    headers=headers,
                    json=specialty_data
                )
                
                print(f"Status da criação de especialidade: {response.status_code}")
                if response.status_code != 200:
                    print(f"Erro: {response.text}")
                else:
                    print("Especialidade criada com sucesso!")
                    
        else:
            print(f"Erro no login: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

def test_frontend_api():
    """Testa a API do frontend"""
    print("\n=== TESTE DA API DO FRONTEND ===")
    
    # Primeiro, fazer login para obter token
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
            
            if token:
                # Teste da API do frontend
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                specialty_data = {
                    "name": "Teste Frontend",
                    "description": "Especialidade via frontend",
                    "code": "FRONT",
                    "is_active": True,
                    "requires_oab": False
                }
                
                response = requests.post(
                    f"{FRONTEND_URL}/api/v1/company/specialties",
                    headers=headers,
                    json=specialty_data
                )
                
                print(f"Status da API do frontend: {response.status_code}")
                print(f"Resposta: {response.text}")
                
        else:
            print(f"Erro no login: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

def check_token_format():
    """Verifica o formato do token"""
    print("\n=== VERIFICAÇÃO DO FORMATO DO TOKEN ===")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/auth/login", json={
            "email": "joao@escritoriodemo.com",
            "password": "123456",
            "tenant_slug": "demo"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            
            if token:
                print(f"Token completo: {token}")
                print(f"Tamanho do token: {len(token)}")
                print(f"Token começa com: {token[:10]}")
                
                # Verificar se é um JWT válido (3 partes separadas por ponto)
                parts = token.split('.')
                print(f"Número de partes do JWT: {len(parts)}")
                
                if len(parts) == 3:
                    print("✅ Token parece ser um JWT válido")
                else:
                    print("❌ Token não parece ser um JWT válido")
                    
        else:
            print(f"Erro no login: {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_backend_auth()
    test_frontend_api()
    check_token_format()
