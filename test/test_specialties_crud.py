#!/usr/bin/env python3
"""
Teste das funcionalidades de CRUD de especialidades
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:3000"
API_BASE = f"{BASE_URL}/api/v1/company/specialties"

def test_specialties_crud():
    """Testa as funcionalidades de CRUD de especialidades"""
    
    print("🧪 Testando CRUD de Especialidades")
    print("=" * 50)
    
    # Teste 1: Listar especialidades
    print("\n1. 📋 Testando listagem de especialidades...")
    try:
        response = requests.get(API_BASE)
        if response.status_code == 200:
            specialties = response.json()
            print(f"✅ Sucesso! {len(specialties)} especialidades encontradas")
            for specialty in specialties:
                print(f"   - {specialty['name']} ({specialty['code']}) - {'Ativa' if specialty['is_active'] else 'Inativa'}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Criar especialidade
    print("\n2. ➕ Testando criação de especialidade...")
    new_specialty = {
        "name": "Direito Digital",
        "description": "Especialidade que trata de questões relacionadas à tecnologia e internet",
        "code": "DIG",
        "color": "#FF6B6B",
        "icon": "computer",
        "display_order": "6",
        "requires_oab": True,
        "min_experience_years": "2"
    }
    
    try:
        response = requests.post(API_BASE, json=new_specialty)
        if response.status_code == 201:
            created_specialty = response.json()
            print(f"✅ Especialidade criada com sucesso! ID: {created_specialty['id']}")
            specialty_id = created_specialty['id']
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return
    
    # Teste 3: Visualizar especialidade
    print("\n3. 👁️ Testando visualização de especialidade...")
    try:
        response = requests.get(f"{API_BASE}?id={specialty_id}")
        if response.status_code == 200:
            specialty = response.json()
            print(f"✅ Especialidade encontrada: {specialty['name']} ({specialty['code']})")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: Atualizar especialidade
    print("\n4. ✏️ Testando atualização de especialidade...")
    update_data = {
        "id": specialty_id,
        "name": "Direito Digital e Tecnologia",
        "description": "Especialidade atualizada que trata de questões relacionadas à tecnologia, internet e inovação",
        "min_experience_years": "3"
    }
    
    try:
        response = requests.put(API_BASE, json=update_data)
        if response.status_code == 200:
            updated_specialty = response.json()
            print(f"✅ Especialidade atualizada: {updated_specialty['name']} - Exp: {updated_specialty['min_experience_years']} anos")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 5: Excluir especialidade
    print("\n5. 🗑️ Testando exclusão de especialidade...")
    try:
        response = requests.delete(f"{API_BASE}?id={specialty_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Especialidade excluída: {result['message']}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 6: Verificar se especialidade foi excluída
    print("\n6. 🔍 Verificando se especialidade foi excluída...")
    try:
        response = requests.get(f"{API_BASE}?id={specialty_id}")
        if response.status_code == 404:
            print("✅ Especialidade não encontrada (excluída corretamente)")
        else:
            print(f"⚠️ Especialidade ainda existe: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Teste concluído!")

def test_stats():
    """Testa as estatísticas de especialidades"""
    print("\n📊 Testando estatísticas de especialidades...")
    
    try:
        response = requests.get(f"{API_BASE}/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas carregadas:")
            print(f"   - Total: {stats.get('total_specialties', 0)}")
            print(f"   - Ativas: {stats.get('active_specialties', 0)}")
            print(f"   - Inativas: {stats.get('inactive_specialties', 0)}")
            print(f"   - Requerem OAB: {stats.get('specialties_with_oab_requirement', 0)}")
            print(f"   - Com experiência: {stats.get('specialties_with_experience_requirement', 0)}")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Executar testes
    test_specialties_crud()
    test_stats()
