#!/usr/bin/env python3
"""
Teste específico para o frontend do Super Admin
"""

import requests
import json
import time

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_superadmin_login_frontend():
    """Testa o login do super admin no frontend"""
    print("🔍 Testando login do super admin no frontend...")
    
    try:
        # Primeiro, fazer login via API para obter token
        login_data = {
            "email": "admin@saasjuridico.com",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/auth/superadmin/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if response.status_code != 200:
            print(f"❌ Erro no login da API: {response.status_code}")
            return False
        
        token_data = response.json()
        token = token_data['access_token']
        print(f"✅ Token obtido: {token[:50]}...")
        
        # Testar acesso ao dashboard
        dashboard_response = requests.get(
            f"{FRONTEND_URL}/superadmin/dashboard",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard acessível")
            return True
        else:
            print(f"❌ Erro ao acessar dashboard: {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_superadmin_pages():
    """Testa as páginas do super admin"""
    print("🔍 Testando páginas do super admin...")
    
    pages = [
        "/superadmin/login",
        "/superadmin/dashboard",
        "/superadmin/tenants"
    ]
    
    for page in pages:
        try:
            response = requests.get(f"{FRONTEND_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {page} - OK")
            else:
                print(f"❌ {page} - Erro {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Testando frontend do Super Admin...")
    print("=" * 50)
    
    # Teste 1: Páginas básicas
    test_superadmin_pages()
    
    print("\n" + "=" * 50)
    
    # Teste 2: Login e dashboard
    if test_superadmin_login_frontend():
        print("✅ Frontend do Super Admin funcionando!")
    else:
        print("❌ Problemas no frontend do Super Admin")
    
    print("\n" + "=" * 50)
    print("🔗 URLs de acesso:")
    print(f"   - Login: {FRONTEND_URL}/superadmin/login")
    print(f"   - Dashboard: {FRONTEND_URL}/superadmin/dashboard")
    print(f"   - Empresas: {FRONTEND_URL}/superadmin/tenants")

if __name__ == "__main__":
    main()
