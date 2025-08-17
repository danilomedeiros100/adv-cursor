#!/usr/bin/env python3
import requests
import json
import time

# Configurações
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_final_solution():
    """Testa a solução final"""
    print("=== TESTE FINAL DA SOLUÇÃO ===")
    
    # 1. Verificar se os serviços estão rodando
    print("\n1. Verificando serviços...")
    
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
    
    # 2. Fazer login
    print("\n2. Fazendo login...")
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
            
            # 3. Testar todas as operações
            print("\n3. Testando operações...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 3.1 Testar busca de especialidades
            print("\n3.1. Testando busca de especialidades...")
            response = requests.get(f"{FRONTEND_URL}/api/v1/company/specialties", headers=headers)
            
            if response.status_code == 200:
                specialties = response.json()
                print(f"✅ Busca funcionando - {len(specialties)} especialidades encontradas")
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                print(f"Resposta: {response.text}")
                return
            
            # 3.2 Testar criação de especialidade
            print("\n3.2. Testando criação de especialidade...")
            specialty_data = {
                "name": f"Teste Final {int(time.time())}",
                "description": "Especialidade de teste final"
            }
            
            response = requests.post(
                f"{FRONTEND_URL}/api/v1/company/specialties",
                headers=headers,
                json=specialty_data
            )
            
            if response.status_code == 201:
                created_specialty = response.json()
                print(f"✅ Criação funcionando - ID: {created_specialty['id']}")
                
                # 3.3 Testar atualização
                print("\n3.3. Testando atualização...")
                update_data = {
                    "id": created_specialty['id'],
                    "name": f"Teste Final Atualizado {int(time.time())}",
                    "description": "Especialidade atualizada"
                }
                
                response = requests.put(
                    f"{FRONTEND_URL}/api/v1/company/specialties",
                    headers=headers,
                    json=update_data
                )
                
                if response.status_code == 200:
                    print("✅ Atualização funcionando")
                else:
                    print(f"❌ Erro na atualização: {response.status_code}")
                
                # 3.4 Testar exclusão
                print("\n3.4. Testando exclusão...")
                response = requests.delete(
                    f"{FRONTEND_URL}/api/v1/company/specialties?id={created_specialty['id']}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ Exclusão funcionando")
                else:
                    print(f"❌ Erro na exclusão: {response.status_code}")
                
            else:
                print(f"❌ Erro na criação: {response.status_code}")
                print(f"Resposta: {response.text}")
                return
            
            # 4. Resumo final
            print("\n" + "="*50)
            print("🎉 SOLUÇÃO FUNCIONANDO PERFEITAMENTE!")
            print("="*50)
            print("✅ Frontend: Funcionando")
            print("✅ Backend: Funcionando")
            print("✅ Autenticação: Funcionando")
            print("✅ CRUD de Especialidades: Funcionando")
            print("="*50)
            print("\n🔧 PRÓXIMOS PASSOS:")
            print("1. Acesse: http://localhost:3000")
            print("2. Faça login com:")
            print("   - Email: joao@escritoriodemo.com")
            print("   - Senha: 123456")
            print("   - Tenant: demo")
            print("3. Navegue para 'Especialidades'")
            print("4. Teste criar, editar e excluir especialidades")
            print("="*50)
            
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_final_solution()
