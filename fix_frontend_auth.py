#!/usr/bin/env python3
import requests
import json
import time

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def fix_frontend_auth():
    """Verifica e corrige a autenticação no frontend"""
    print("=== VERIFICAÇÃO E CORREÇÃO DA AUTENTICAÇÃO ===")
    
    # 1. Verificar se o frontend está rodando
    print("\n1. Verificando se o frontend está rodando...")
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend está rodando")
        else:
            print(f"❌ Frontend retornou status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao acessar frontend: {e}")
        return
    
    # 2. Verificar se o backend está rodando
    print("\n2. Verificando se o backend está rodando...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando")
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro ao acessar backend: {e}")
        return
    
    # 3. Fazer login para obter token válido
    print("\n3. Fazendo login para obter token válido...")
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
            
            # 4. Testar se o token funciona
            print("\n4. Testando se o token funciona...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Testar busca de especialidades
            response = requests.get(f"{FRONTEND_URL}/api/v1/company/specialties", headers=headers)
            
            if response.status_code == 200:
                print("✅ Token está funcionando corretamente!")
                
                # 5. Instruções para o usuário
                print("\n" + "="*50)
                print("🔧 INSTRUÇÕES PARA CORRIGIR O PROBLEMA:")
                print("="*50)
                print("1. Abra o navegador e acesse: http://localhost:3000")
                print("2. Clique em 'Login' no canto superior direito")
                print("3. Use as seguintes credenciais:")
                print("   - Email: joao@escritoriodemo.com")
                print("   - Senha: 123456")
                print("   - Tenant: demo")
                print("4. Após fazer login, navegue para 'Especialidades'")
                print("5. Teste criar uma nova especialidade")
                print("="*50)
                
                # 6. Testar criação de especialidade
                print("\n5. Testando criação de especialidade...")
                
                specialty_data = {
                    "name": f"Teste {int(time.time())}",
                    "description": "Especialidade de teste"
                }
                
                response = requests.post(
                    f"{FRONTEND_URL}/api/v1/company/specialties",
                    headers=headers,
                    json=specialty_data
                )
                
                if response.status_code == 201:
                    print("✅ Criação de especialidade funcionando!")
                else:
                    print(f"❌ Erro na criação: {response.status_code}")
                    print(f"Resposta: {response.text}")
                    
            else:
                print(f"❌ Token não está funcionando: {response.status_code}")
                print(f"Resposta: {response.text}")
                
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    fix_frontend_auth()
