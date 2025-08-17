#!/usr/bin/env python3
import requests
import json
import time

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3002"

def test_complete_flow():
    print("🧪 Teste Completo: Login + CRUD Especialidades")
    print("=" * 60)
    
    # 1. Fazer login
    print("1. Fazendo login...")
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
            print(f"Token obtido: {token[:20]}...")
        else:
            print(f"❌ Erro no login: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return
    
    # 2. Testar API de especialidades
    print("\n2. Testando API de especialidades...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Listar especialidades
    try:
        list_response = requests.get(f"{BACKEND_URL}/api/v1/company/specialties/", headers=headers)
        print(f"Status da listagem: {list_response.status_code}")
        
        if list_response.status_code == 200:
            specialties = list_response.json()
            print(f"✅ Especialidades encontradas: {len(specialties)}")
            for spec in specialties:
                print(f"  - {spec.get('name', 'N/A')}")
        else:
            print(f"❌ Erro ao listar especialidades: {list_response.text}")
    except Exception as e:
        print(f"❌ Erro ao listar especialidades: {e}")
    
    # 3. Criar nova especialidade
    print("\n3. Criando nova especialidade...")
    new_specialty = {
        "name": "Direito Trabalhista",
        "description": "Especialidade em direito do trabalho",
        "code": "TRAB",
        "color": "#FF6B6B",
        "icon": "briefcase",
        "display_order": "1",
        "requires_oab": True,
        "min_experience_years": "2"
    }
    
    try:
        create_response = requests.post(f"{BACKEND_URL}/api/v1/company/specialties/", 
                                      headers=headers, json=new_specialty)
        print(f"Status da criação: {create_response.status_code}")
        
        if create_response.status_code == 201:
            created_specialty = create_response.json()
            print(f"✅ Especialidade criada com sucesso!")
            print(f"  ID: {created_specialty.get('id')}")
            print(f"  Nome: {created_specialty.get('name')}")
        else:
            print(f"❌ Erro ao criar especialidade: {create_response.text}")
    except Exception as e:
        print(f"❌ Erro ao criar especialidade: {e}")
    
    # 4. Testar frontend
    print("\n4. Testando frontend...")
    print(f"Frontend rodando em: {FRONTEND_URL}")
    print("Para testar manualmente:")
    print(f"1. Acesse: {FRONTEND_URL}/auth/login")
    print("2. Use as credenciais:")
    print(f"   Email: {login_data['email']}")
    print(f"   Senha: {login_data['password']}")
    print(f"   Tenant: {login_data['tenant_slug']}")
    print("3. Após login, acesse: /company/specialties")
    
    return token

if __name__ == "__main__":
    token = test_complete_flow()
    if token:
        print(f"\n🎉 Teste concluído! Token válido: {token[:20]}...")
    else:
        print("\n❌ Teste falhou!")
