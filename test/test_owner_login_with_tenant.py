#!/usr/bin/env python3
"""
Script para testar login do owner com tenant_slug
"""
import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api/v1"

def test_owner_login_with_tenant():
    """Testa login do owner com tenant_slug"""
    
    # Dados do último owner criado
    owner_email = "maria-1755302373@escritorioteste.com"
    owner_password = "123456"
    tenant_slug = "escritorio-teste-owner-1755302373"
    
    print("🧪 Testando login do owner com tenant_slug...")
    print(f"   Email: {owner_email}")
    print(f"   Tenant Slug: {tenant_slug}")
    
    # Teste 1: Login sem tenant_slug
    login_data = {
        "email": owner_email,
        "password": owner_password
    }
    
    response = requests.post(f"{BASE_URL}/auth/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login do owner realizado com sucesso (sem tenant_slug)!")
        print(f"   Token: {result['access_token'][:50]}...")
        return True
    else:
        print(f"❌ Erro no login do owner (sem tenant_slug): {response.status_code}")
        print(f"   Resposta: {response.text}")
    
    # Teste 2: Login com tenant_slug
    login_data_with_tenant = {
        "email": owner_email,
        "password": owner_password,
        "tenant_slug": tenant_slug
    }
    
    response2 = requests.post(f"{BASE_URL}/auth/auth/login", json=login_data_with_tenant)
    
    if response2.status_code == 200:
        result = response2.json()
        print("✅ Login do owner realizado com sucesso (com tenant_slug)!")
        print(f"   Token: {result['access_token'][:50]}...")
        tenant = result.get('tenant')
        if tenant:
            print(f"   Tenant: {tenant.get('name', 'N/A')}")
        return True
    else:
        print(f"❌ Erro no login do owner (com tenant_slug): {response2.status_code}")
        print(f"   Resposta: {response2.text}")
        return False

if __name__ == "__main__":
    test_owner_login_with_tenant()
