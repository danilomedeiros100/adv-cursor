#!/usr/bin/env python3
"""
Script para testar criação de clientes diretamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from core.database import SessionLocal
from core.models.client import Client
from apps.clients.schemas import ClientCreate
import uuid

def test_create_client():
    """Testa criação de cliente diretamente"""
    db = SessionLocal()
    
    try:
        print("🔧 Testando criação de cliente...")
        
        # Dados do cliente
        client_data = ClientCreate(
            name="João Silva Teste",
            email="joao.teste@teste.com",
            phone="11999999999",
            cpf_cnpj="12345678901",
            person_type="PF"
        )
        
        # Tenant ID (usando o mesmo do teste anterior)
        tenant_id = uuid.UUID("3c3b6ff1-3879-47ee-bcc3-b881597fdfff")
        
        print(f"   Nome: {client_data.name}")
        print(f"   Email: {client_data.email}")
        print(f"   Tenant ID: {tenant_id}")
        
        # Criar cliente
        client = Client(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=client_data.name,
            email=client_data.email,
            phone=client_data.phone,
            cpf_cnpj=client_data.cpf_cnpj,
            person_type=client_data.person_type
        )
        
        print("   Cliente criado em memória")
        
        # Adicionar ao banco
        db.add(client)
        db.commit()
        db.refresh(client)
        
        print(f"   Cliente salvo no banco com ID: {client.id}")
        print("✅ Cliente criado com sucesso!")
        
        # Verificar se foi salvo
        saved_client = db.query(Client).filter(Client.id == client.id).first()
        if saved_client:
            print(f"   Cliente encontrado no banco: {saved_client.name}")
        else:
            print("❌ Cliente não encontrado no banco")
        
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_create_client()
