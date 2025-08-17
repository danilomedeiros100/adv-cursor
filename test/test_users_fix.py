#!/usr/bin/env python3
"""
Script para testar se o problema de carregamento de usuários foi resolvido
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"
LOGIN_EMAIL = "maria-1755302373@escritorioteste.com"
LOGIN_PASSWORD = "123456"

def test_login_and_users():
    """Testa login e depois carrega usuários"""
    
    print("🔍 Testando login e carregamento de usuários...")
    
    # 1. Fazer login
    print("\n1. Fazendo login...")
    login_data = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            return False
            
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        
        if not access_token:
            print("❌ Token não encontrado na resposta")
            return False
            
        print(f"✅ Login realizado com sucesso!")
        print(f"Token: {access_token[:50]}...")
        
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return False
    
    # 2. Testar rota de usuários
    print("\n2. Testando rota de usuários...")
    
    try:
        users_response = requests.get(
            f"{BASE_URL}/company/users/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if users_response.status_code != 200:
            print(f"❌ Erro ao carregar usuários: {users_response.status_code}")
            print(f"Resposta: {users_response.text}")
            return False
            
        users_data = users_response.json()
        print(f"✅ Usuários carregados com sucesso!")
        print(f"Total de usuários: {len(users_data)}")
        
        for user in users_data:
            print(f"  - {user.get('name')} ({user.get('email')}) - {user.get('role', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro ao carregar usuários: {e}")
        return False
    
    # 3. Testar estatísticas
    print("\n3. Testando estatísticas de usuários...")
    
    try:
        stats_response = requests.get(
            f"{BASE_URL}/company/users/stats/summary",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if stats_response.status_code != 200:
            print(f"❌ Erro ao carregar estatísticas: {stats_response.status_code}")
            print(f"Resposta: {stats_response.text}")
            return False
            
        stats_data = stats_response.json()
        print(f"✅ Estatísticas carregadas com sucesso!")
        print(f"Total de usuários: {stats_data.get('total_users')}")
        print(f"Usuários ativos: {stats_data.get('active_users')}")
        print(f"Advogados: {stats_data.get('role_counts', {}).get('lawyer', 0)}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar estatísticas: {e}")
        return False
    
    # 4. Testar departamentos
    print("\n4. Testando lista de departamentos...")
    
    try:
        dept_response = requests.get(
            f"{BASE_URL}/company/users/departments/list",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if dept_response.status_code != 200:
            print(f"❌ Erro ao carregar departamentos: {dept_response.status_code}")
            print(f"Resposta: {dept_response.text}")
            return False
            
        dept_data = dept_response.json()
        print(f"✅ Departamentos carregados com sucesso!")
        print(f"Departamentos: {dept_data.get('departments', [])}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar departamentos: {e}")
        return False
    
    print("\n🎉 Todos os testes passaram! O problema foi resolvido.")
    return True

if __name__ == "__main__":
    success = test_login_and_users()
    if not success:
        print("\n❌ Alguns testes falharam. Verifique os logs acima.")
        exit(1)
