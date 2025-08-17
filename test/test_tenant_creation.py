#!/usr/bin/env python3
"""
Script para testar a criação de tenant com usuário owner
"""
import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000/api/v1"
SUPER_ADMIN_EMAIL = "admin@saasjuridico.com"
SUPER_ADMIN_PASSWORD = "admin123"

# Gerar timestamp único para evitar conflitos
TIMESTAMP = int(time.time())

def login_super_admin():
    """Faz login como Super Admin"""
    login_data = {
        "email": SUPER_ADMIN_EMAIL,
        "password": SUPER_ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/auth/superadmin/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login do Super Admin realizado com sucesso")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code} - {response.text}")
        return None

def create_tenant_with_owner(token):
    """Cria um tenant com usuário owner"""
    tenant_data = {
        "name": f"Escritório Teste Owner {TIMESTAMP}",
        "slug": f"escritorio-teste-owner-{TIMESTAMP}",
        "email": f"contato-{TIMESTAMP}@escritorioteste.com",
        "phone": "(11) 55555-5555",
        "plan_type": "premium",
        "max_users": 20,
        "max_processes": 500,
        # Dados do usuário owner
        "owner_name": f"Maria Silva {TIMESTAMP}",
        "owner_email": f"maria-{TIMESTAMP}@escritorioteste.com",
        "owner_password": "123456",
        "owner_phone": "(11) 44444-4444",
        "owner_oab_number": "789012",
        "owner_oab_state": "SP",
        "owner_position": "Advogada",
        "owner_department": "Civil"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/superadmin/super-admin/tenants", 
                           json=tenant_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Tenant criado com sucesso!")
        print(f"   ID: {result['id']}")
        print(f"   Nome: {result['name']}")
        print(f"   Slug: {result['slug']}")
        print(f"   Owner criado: {result.get('owner_created', False)}")
        print(f"   Email do owner: {result.get('owner_email', 'N/A')}")
        return result
    else:
        print(f"❌ Erro ao criar tenant: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return None

def test_owner_login(tenant_slug, owner_email, owner_password):
    """Testa o login do usuário owner"""
    # Primeiro, tentar login sem tenant_slug
    login_data = {
        "email": owner_email,
        "password": owner_password
    }
    
    response = requests.post(f"{BASE_URL}/auth/auth/login", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login do owner realizado com sucesso!")
        print(f"   Token: {result['access_token'][:50]}...")
        print(f"   Tenant: {result.get('tenant', {}).get('name', 'N/A')}")
        return result
    else:
        print(f"❌ Erro no login do owner: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        # Tentar com tenant_slug
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
            print(f"   Tenant: {result.get('tenant', {}).get('name', 'N/A')}")
            return result
        else:
            print(f"❌ Erro no login do owner (com tenant_slug): {response2.status_code}")
            print(f"   Resposta: {response2.text}")
            return None

def main():
    """Função principal"""
    print("🧪 Testando criação de tenant com usuário owner")
    print("=" * 50)
    
    # 1. Login como Super Admin
    print("\n1. Fazendo login como Super Admin...")
    token = login_super_admin()
    if not token:
        return
    
    # 2. Criar tenant com owner
    print("\n2. Criando tenant com usuário owner...")
    tenant = create_tenant_with_owner(token)
    if not tenant:
        return
    
    # 3. Testar login do owner
    print("\n3. Testando login do usuário owner...")
    owner_login = test_owner_login(
        tenant['slug'],
        tenant['owner_email'],
        "123456"  # senha definida no create_tenant_with_owner
    )
    
    if owner_login:
        print("\n🎉 Teste concluído com sucesso!")
        print("   O problema dos usuários owner sem senha foi resolvido!")
    else:
        print("\n❌ Teste falhou!")
        print("   O problema ainda persiste.")

if __name__ == "__main__":
    main()
