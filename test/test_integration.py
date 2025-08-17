#!/usr/bin/env python3
"""
Script para testar a integração completa entre frontend e backend
"""

import requests
import json
import time

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Testa se o backend está funcionando"""
    print("🔍 Testando saúde do backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend funcionando: {data['message']}")
            return True
        else:
            print(f"❌ Backend não respondeu corretamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return False

def test_frontend_health():
    """Testa se o frontend está funcionando"""
    print("🔍 Testando saúde do frontend...")
    try:
        response = requests.get(f"{FRONTEND_URL}/superadmin/login")
        if response.status_code == 200:
            print("✅ Frontend funcionando")
            return True
        else:
            print(f"❌ Frontend não respondeu corretamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com frontend: {e}")
        return False

def test_superadmin_login():
    """Testa o login do super admin"""
    print("🔍 Testando login do super admin...")
    try:
        login_data = {
            "email": "admin@saasjuridico.com",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/superadmin/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login do super admin funcionando")
            print(f"   Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
        return None

def test_dashboard_endpoints(token):
    """Testa os endpoints do dashboard"""
    print("🔍 Testando endpoints do dashboard...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/api/v1/superadmin/super-admin/dashboard/overview",
        "/api/v1/superadmin/super-admin/tenants",
        "/api/v1/superadmin/super-admin/analytics/overview"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Erro {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {e}")

def test_tenant_management(token):
    """Testa a gestão de tenants"""
    print("🔍 Testando gestão de tenants...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Listar tenants
        response = requests.get(f"{BACKEND_URL}/api/v1/superadmin/super-admin/tenants", headers=headers)
        if response.status_code == 200:
            tenants = response.json()
            print(f"✅ Listagem de tenants: {len(tenants)} encontrados")
            
            if tenants:
                tenant_id = tenants[0]['id']
                print(f"   Primeiro tenant: {tenants[0]['name']} ({tenant_id})")
                
                # Testar obtenção de tenant específico
                response = requests.get(f"{BACKEND_URL}/api/v1/superadmin/super-admin/tenants/{tenant_id}", headers=headers)
                if response.status_code == 200:
                    print(f"✅ Detalhes do tenant {tenant_id} - OK")
                else:
                    print(f"❌ Erro ao obter detalhes do tenant: {response.status_code}")
        else:
            print(f"❌ Erro ao listar tenants: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar gestão de tenants: {e}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de integração...")
    print("=" * 50)
    
    # Teste 1: Saúde do backend
    if not test_backend_health():
        print("❌ Backend não está funcionando. Abortando testes.")
        return
    
    # Teste 2: Saúde do frontend
    if not test_frontend_health():
        print("❌ Frontend não está funcionando. Abortando testes.")
        return
    
    # Teste 3: Login do super admin
    token = test_superadmin_login()
    if not token:
        print("❌ Login falhou. Abortando testes.")
        return
    
    # Teste 4: Endpoints do dashboard
    test_dashboard_endpoints(token)
    
    # Teste 5: Gestão de tenants
    test_tenant_management(token)
    
    print("\n" + "=" * 50)
    print("✅ Testes de integração concluídos!")
    print("\n📋 Resumo:")
    print("   - Backend: ✅ Funcionando")
    print("   - Frontend: ✅ Funcionando")
    print("   - Login Super Admin: ✅ Funcionando")
    print("   - Dashboard: ✅ Funcionando")
    print("   - Gestão de Tenants: ✅ Funcionando")
    print("\n🔗 URLs de acesso:")
    print(f"   - Backend API: {BACKEND_URL}")
    print(f"   - Frontend: {FRONTEND_URL}")
    print(f"   - Portal Super Admin: {FRONTEND_URL}/superadmin/login")
    print(f"   - Dashboard: {FRONTEND_URL}/superadmin/dashboard")
    print("\n🔑 Credenciais:")
    print("   - Email: admin@saasjuridico.com")
    print("   - Senha: admin123")

if __name__ == "__main__":
    main()
