#!/usr/bin/env python3
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
SPECIALTIES_URL = f"{BASE_URL}/api/v1/company/specialties"

def test_localstorage_debug():
    print("🔍 Debug do localStorage e Autenticação")
    print("=" * 50)
    
    # 1. Testar login como empresa
    print("1. Testando login como empresa...")
    login_data = {
        "email": "contato@empresa.com",  # Substitua pelo email da empresa
        "password": "123456",  # Substitua pela senha da empresa
        "tenant_slug": "empresa-teste"  # Substitua pelo slug da empresa
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login realizado com sucesso!")
            print(f"Token: {token[:20]}...")
            print(f"User: {login_result.get('user', {}).get('name')}")
            print(f"Tenant: {login_result.get('tenant', {}).get('name') if login_result.get('tenant') else 'Nenhum'}")
            
            # 2. Testar API de especialidades
            print("\n2. Testando API de especialidades...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            specialties_response = requests.get(SPECIALTIES_URL, headers=headers)
            print(f"Status da API: {specialties_response.status_code}")
            
            if specialties_response.status_code == 200:
                specialties = specialties_response.json()
                print(f"✅ API funcionando! Especialidades encontradas: {len(specialties)}")
            else:
                print(f"❌ Erro na API: {specialties_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_localstorage_debug()
