#!/usr/bin/env python3
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
SPECIALTIES_URL = f"{BASE_URL}/api/v1/company/specialties"

def test_specialties_api():
    print("🧪 Testando API de Especialidades")
    print("=" * 50)
    
    # 1. Fazer login como empresa
    print("1. Fazendo login como empresa...")
    login_data = {
        "email": "admin@saasjuridico.com",
        "password": "123456",
        "tenant_slug": "demo-empresa"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status do login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            print(f"✅ Login realizado com sucesso!")
            print(f"Token: {token[:20]}...")
            
            # 2. Testar listagem de especialidades
            print("\n2. Testando listagem de especialidades...")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            specialties_response = requests.get(SPECIALTIES_URL, headers=headers)
            print(f"Status da listagem: {specialties_response.status_code}")
            
            if specialties_response.status_code == 200:
                specialties = specialties_response.json()
                print(f"✅ Especialidades encontradas: {len(specialties)}")
                for specialty in specialties:
                    print(f"  - {specialty.get('name')} (ID: {specialty.get('id')})")
            else:
                print(f"❌ Erro na listagem: {specialties_response.text}")
                
            # 3. Testar criação de especialidade
            print("\n3. Testando criação de especialidade...")
            new_specialty = {
                "name": "Direito Civil",
                "description": "Especialidade em direito civil",
                "code": "CIV",
                "color": "#3B82F6",
                "display_order": "1",
                "requires_oab": True,
                "min_experience_years": "3"
            }
            
            create_response = requests.post(SPECIALTIES_URL, json=new_specialty, headers=headers)
            print(f"Status da criação: {create_response.status_code}")
            
            if create_response.status_code == 201:
                created_specialty = create_response.json()
                print(f"✅ Especialidade criada: {created_specialty.get('name')} (ID: {created_specialty.get('id')})")
                
                # 4. Testar atualização
                print("\n4. Testando atualização...")
                update_data = {
                    "name": "Direito Civil Atualizado",
                    "description": "Descrição atualizada"
                }
                
                update_response = requests.put(
                    f"{SPECIALTIES_URL}/{created_specialty.get('id')}", 
                    json=update_data, 
                    headers=headers
                )
                print(f"Status da atualização: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    print("✅ Especialidade atualizada com sucesso!")
                else:
                    print(f"❌ Erro na atualização: {update_response.text}")
                    
                # 5. Testar exclusão
                print("\n5. Testando exclusão...")
                delete_response = requests.delete(
                    f"{SPECIALTIES_URL}/{created_specialty.get('id')}", 
                    headers=headers
                )
                print(f"Status da exclusão: {delete_response.status_code}")
                
                if delete_response.status_code == 200:
                    print("✅ Especialidade excluída com sucesso!")
                else:
                    print(f"❌ Erro na exclusão: {delete_response.text}")
                    
            else:
                print(f"❌ Erro na criação: {create_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_specialties_api()
