#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_create_tenant():
    """Testa a criação de novos tenants"""
    print("🚀 Testando criação de Tenants...")
    print("=" * 50)
    
    # 1. Login do Super Admin
    print("🔑 Fazendo login do Super Admin...")
    login_data = {
        "email": "admin@saasjuridico.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/auth/superadmin/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login realizado com sucesso")
    
    # 2. Listar tenants existentes
    print("\n📋 Listando tenants existentes...")
    response = requests.get(f"{BASE_URL}/superadmin/super-admin/tenants", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erro ao listar tenants: {response.status_code}")
        return
    
    existing_tenants = response.json()
    print(f"✅ Encontrados {len(existing_tenants)} tenants existentes")
    
    # 3. Criar novo tenant
    print("\n➕ Criando novo tenant...")
    new_tenant_data = {
        "name": "Escritório Teste",
        "slug": "escritorio-teste",
        "email": "contato@escritorioteste.com",
        "phone": "(11) 99999-8888",
        "plan_type": "premium",
        "max_users": 25,
        "max_processes": 500
    }
    
    response = requests.post(
        f"{BASE_URL}/superadmin/super-admin/tenants",
        json=new_tenant_data,
        headers=headers
    )
    
    if response.status_code == 200:
        new_tenant = response.json()
        print("✅ Tenant criado com sucesso!")
        print(f"   ID: {new_tenant['id']}")
        print(f"   Nome: {new_tenant['name']}")
        print(f"   Email: {new_tenant['email']}")
        print(f"   Plano: {new_tenant['plan_type']}")
        print(f"   Status: {'Ativo' if new_tenant['is_active'] else 'Inativo'}")
        
        # 4. Verificar se o tenant foi criado
        print(f"\n🔍 Verificando se o tenant foi criado...")
        response = requests.get(
            f"{BASE_URL}/superadmin/super-admin/tenants/{new_tenant['id']}",
            headers=headers
        )
        
        if response.status_code == 200:
            tenant_details = response.json()
            print("✅ Tenant encontrado no sistema")
            print(f"   Nome: {tenant_details['name']}")
            print(f"   Slug: {tenant_details['slug']}")
            print(f"   Configurações: {tenant_details['settings']}")
        else:
            print(f"❌ Erro ao buscar tenant: {response.status_code}")
        
        # 5. Listar tenants novamente para confirmar
        print(f"\n📋 Listando tenants após criação...")
        response = requests.get(f"{BASE_URL}/superadmin/super-admin/tenants", headers=headers)
        if response.status_code == 200:
            updated_tenants = response.json()
            print(f"✅ Agora temos {len(updated_tenants)} tenants")
            
            # Verificar se o novo tenant está na lista
            new_tenant_found = any(t['id'] == new_tenant['id'] for t in updated_tenants)
            if new_tenant_found:
                print("✅ Novo tenant encontrado na listagem")
            else:
                print("❌ Novo tenant não encontrado na listagem")
        else:
            print(f"❌ Erro ao listar tenants: {response.status_code}")
            
    elif response.status_code == 400:
        error_data = response.json()
        print(f"❌ Erro de validação: {error_data.get('detail', 'Erro desconhecido')}")
    else:
        print(f"❌ Erro ao criar tenant: {response.status_code}")
        print(f"   Resposta: {response.text}")
    
    print("\n" + "=" * 50)
    print("✅ Teste de criação de Tenant concluído!")

if __name__ == "__main__":
    # Aguardar um pouco para o backend inicializar
    print("⏳ Aguardando backend inicializar...")
    time.sleep(3)
    test_create_tenant()
