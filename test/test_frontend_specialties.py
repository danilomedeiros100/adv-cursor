#!/usr/bin/env python3
import requests
import json

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_frontend_specialties():
    print("🧪 Testando Frontend -> Backend de Especialidades")
    print("=" * 60)
    
    # 1. Fazer login como empresa
    print("1. Simulando login no frontend...")
    
    # Primeiro, vamos tentar fazer login diretamente no backend
    login_data = {
        "email": "joao.silva@escritorioteste.com.br",
        "password": "123456",
        "tenant_slug": "escritorio-teste"
    }
    
    try:
        # Tentar login no backend
        login_response = requests.post(f"{BACKEND_URL}/api/v1/auth/auth/login", json=login_data)
        print(f"Status do login no backend: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login realizado com sucesso!")
            print(f"Token: {token[:20]}...")
            
            # 2. Testar API de especialidades via frontend
            print("\n2. Testando API de especialidades via frontend...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Testar GET especialidades
            specialties_response = requests.get(f"{FRONTEND_URL}/api/v1/company/specialties", headers=headers)
            print(f"Status da listagem via frontend: {specialties_response.status_code}")
            
            if specialties_response.status_code == 200:
                specialties = specialties_response.json()
                print(f"✅ Especialidades encontradas via frontend: {len(specialties)}")
            else:
                print(f"❌ Erro na listagem via frontend: {specialties_response.text}")
                
            # 3. Testar criação via frontend
            print("\n3. Testando criação via frontend...")
            new_specialty = {
                "name": "Direito Civil Teste",
                "description": "Especialidade em direito civil para teste",
                "code": "CIV_TEST",
                "color": "#3B82F6",
                "display_order": "1",
                "requires_oab": True,
                "min_experience_years": "3"
            }
            
            create_response = requests.post(f"{FRONTEND_URL}/api/v1/company/specialties", json=new_specialty, headers=headers)
            print(f"Status da criação via frontend: {create_response.status_code}")
            
            if create_response.status_code == 201:
                created_specialty = create_response.json()
                print(f"✅ Especialidade criada via frontend: {created_specialty.get('name')}")
            else:
                print(f"❌ Erro na criação via frontend: {create_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_frontend_specialties()
