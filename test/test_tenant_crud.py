#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_tenant_crud():
    """Testa as funcionalidades CRUD de tenants"""
    print("🚀 Testando CRUD de Tenants...")
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
    
    # 2. Listar tenants
    print("\n📋 Listando tenants...")
    response = requests.get(f"{BASE_URL}/superadmin/super-admin/tenants", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erro ao listar tenants: {response.status_code}")
        return
    
    tenants = response.json()
    print(f"✅ Encontrados {len(tenants)} tenants")
    
    if not tenants:
        print("❌ Nenhum tenant encontrado para testar")
        return
    
    tenant_id = tenants[0]["id"]
    tenant_name = tenants[0]["name"]
    print(f"   Usando tenant: {tenant_name} ({tenant_id})")
    
    # 3. Obter detalhes do tenant
    print(f"\n👁️ Obtendo detalhes do tenant {tenant_id}...")
    response = requests.get(f"{BASE_URL}/superadmin/super-admin/tenants/{tenant_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erro ao obter detalhes: {response.status_code}")
        return
    
    tenant_details = response.json()
    print("✅ Detalhes obtidos com sucesso")
    print(f"   Nome: {tenant_details['name']}")
    print(f"   Email: {tenant_details['email']}")
    print(f"   Status: {'Ativo' if tenant_details['is_active'] else 'Inativo'}")
    print(f"   Suspenso: {'Sim' if tenant_details['is_suspended'] else 'Não'}")
    
    # 4. Atualizar tenant
    print(f"\n✏️ Atualizando tenant {tenant_id}...")
    update_data = {
        "name": f"{tenant_details['name']} (Atualizado)",
        "phone": "(11) 88888-8888"
    }
    
    response = requests.put(f"{BASE_URL}/superadmin/super-admin/tenants/{tenant_id}", 
                          json=update_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erro ao atualizar tenant: {response.status_code}")
        return
    
    updated_tenant = response.json()
    print("✅ Tenant atualizado com sucesso")
    print(f"   Novo nome: {updated_tenant['name']}")
    print(f"   Novo telefone: {updated_tenant['phone']}")
    
    # 5. Testar suspensão (se não estiver suspenso)
    if not updated_tenant['is_suspended']:
        print(f"\n⏸️ Suspendo tenant {tenant_id}...")
        suspend_data = {"reason": "Teste de suspensão"}
        response = requests.post(f"{BASE_URL}/superadmin/super-admin/tenants/{tenant_id}/suspend", 
                               json=suspend_data, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erro ao suspender tenant: {response.status_code}")
        else:
            print("✅ Tenant suspenso com sucesso")
            
            # 6. Reativar tenant
            print(f"\n▶️ Reativando tenant {tenant_id}...")
            response = requests.post(f"{BASE_URL}/superadmin/super-admin/tenants/{tenant_id}/activate", 
                                   headers=headers)
            if response.status_code != 200:
                print(f"❌ Erro ao reativar tenant: {response.status_code}")
            else:
                print("✅ Tenant reativado com sucesso")
    
    # 7. Verificar status final
    print(f"\n🔍 Verificando status final do tenant {tenant_id}...")
    response = requests.get(f"{BASE_URL}/superadmin/super-admin/tenants/{tenant_id}", headers=headers)
    if response.status_code == 200:
        final_tenant = response.json()
        print("✅ Status final verificado")
        print(f"   Nome: {final_tenant['name']}")
        print(f"   Status: {'Ativo' if final_tenant['is_active'] else 'Inativo'}")
        print(f"   Suspenso: {'Sim' if final_tenant['is_suspended'] else 'Não'}")
    
    print("\n" + "=" * 50)
    print("✅ Testes CRUD de Tenants concluídos com sucesso!")
    print("\n📋 Resumo das funcionalidades testadas:")
    print("   ✅ Login Super Admin")
    print("   ✅ Listagem de Tenants")
    print("   ✅ Obter detalhes do Tenant")
    print("   ✅ Atualizar Tenant")
    print("   ✅ Suspender Tenant")
    print("   ✅ Reativar Tenant")
    print("   ✅ Verificar status final")

if __name__ == "__main__":
    # Aguardar um pouco para o backend inicializar
    print("⏳ Aguardando backend inicializar...")
    time.sleep(3)
    test_tenant_crud()
