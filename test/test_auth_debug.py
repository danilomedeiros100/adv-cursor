#!/usr/bin/env python3
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/auth/me"

def test_auth_debug():
    print("🔍 Debug da Autenticação")
    print("=" * 50)
    
    # 1. Testar login
    print("1. Testando login...")
    login_data = {
        "email": "admin@admin.com",
        "password": "123456"
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
            
            # 2. Testar endpoint /me
            print("\n2. Testando endpoint /me...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            me_response = requests.get(ME_URL, headers=headers)
            print(f"Status do /me: {me_response.status_code}")
            
            if me_response.status_code == 200:
                me_result = me_response.json()
                print(f"✅ /me funcionando!")
                print(f"User: {me_result.get('user', {}).get('name')}")
                print(f"Tenant: {me_result.get('tenant', {}).get('name') if me_result.get('tenant') else 'Nenhum'}")
            else:
                print(f"❌ Erro no /me: {me_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_auth_debug()
