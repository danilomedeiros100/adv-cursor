#!/usr/bin/env python3

from core.database import SessionLocal
from core.models.tenant import Tenant
from apps.superadmin.schemas import TenantResponse
from pydantic import ValidationError

def test_tenants():
    """Testa a listagem de tenants"""
    db = SessionLocal()
    
    try:
        print("🔍 Testando consulta de tenants...")
        
        # Teste 1: Consulta simples
        tenants = db.query(Tenant).all()
        print(f"✅ Encontrados {len(tenants)} tenants")
        
        if tenants:
            tenant = tenants[0]
            print(f"   Primeiro tenant: {tenant.name} ({tenant.id})")
            
            # Teste 2: Verificar campos
            print("🔍 Verificando campos do tenant...")
            print(f"   ID: {tenant.id}")
            print(f"   Name: {tenant.name}")
            print(f"   Email: {tenant.email}")
            print(f"   Plan Type: {tenant.plan_type}")
            print(f"   Is Active: {tenant.is_active}")
            print(f"   Is Suspended: {tenant.is_suspended}")
            print(f"   Created At: {tenant.created_at}")
            
            # Teste 3: Tentar converter para schema
            print("🔍 Testando conversão para schema...")
            try:
                tenant_dict = {
                    "id": str(tenant.id),
                    "name": tenant.name,
                    "slug": tenant.slug,
                    "email": tenant.email,
                    "phone": tenant.phone,
                    "plan_type": tenant.plan_type,
                    "plan_features": tenant.plan_features or {},
                    "max_users": tenant.max_users,
                    "max_processes": tenant.max_processes,
                    "is_active": tenant.is_active,
                    "is_suspended": tenant.is_suspended,
                    "settings": tenant.settings or {},
                    "branding": tenant.branding or {},
                    "created_at": tenant.created_at
                }
                
                tenant_response = TenantResponse(**tenant_dict)
                print("✅ Conversão para schema bem-sucedida")
                print(f"   Tenant Response: {tenant_response.name}")
                
            except ValidationError as e:
                print(f"❌ Erro na validação: {e}")
                for error in e.errors():
                    print(f"   Campo: {error['loc']}, Erro: {error['msg']}")
            except Exception as e:
                print(f"❌ Erro na conversão: {e}")
        
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_tenants()
