#!/usr/bin/env python3
import requests
import json

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_login_frontend():
    print("🧪 Testando Login no Frontend")
    print("=" * 40)
    
    # 1. Testar se o frontend está rodando
    print("1. Verificando se o frontend está rodando...")
    try:
        response = requests.get(FRONTEND_URL)
        print(f"Status do frontend: {response.status_code}")
        if response.status_code == 200:
            print("✅ Frontend está rodando")
        else:
            print("❌ Frontend não está respondendo corretamente")
            return
    except Exception as e:
        print(f"❌ Erro ao acessar frontend: {e}")
        return
    
    # 2. Testar login no backend
    print("\n2. Testando login no backend...")
    login_data = {
        "email": "joao.silva@escritorioteste.com.br",
        "password": "123456",
        "tenant_slug": "escritorio-teste"
    }
    
    try:
        login_response = requests.post(f"{BACKEND_URL}/api/v1/auth/auth/login", json=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login realizado com sucesso!")
            print(f"Token: {token[:20]}...")
            
            # 3. Testar se o token funciona
            print("\n3. Testando se o token funciona...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Testar endpoint de especialidades
            specialties_response = requests.get(f"{BACKEND_URL}/api/v1/company/specialties", headers=headers)
            print(f"Status da API de especialidades: {specialties_response.status_code}")
            
            if specialties_response.status_code == 200:
                print("✅ Token está funcionando corretamente")
            else:
                print(f"❌ Token não está funcionando: {specialties_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_login_frontend()
