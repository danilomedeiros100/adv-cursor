#!/usr/bin/env python3
"""
Script para limpar toda a base de dados de forma mais robusta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import SessionLocal, engine
from core.models.superadmin import SuperAdmin
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def clear_database_force():
    """Limpa toda a base de dados de forma forçada"""
    db = SessionLocal()
    
    try:
        print("🗑️  Limpando base de dados de forma forçada...")
        
        # Desabilitar constraints temporariamente
        print("   🔧 Desabilitando constraints...")
        db.execute(text("SET session_replication_role = replica;"))
        
        # Lista de todas as tabelas para limpar
        tables_to_clear = [
            "temporary_permissions",
            "audit_logs", 
            "notifications",
            "financial_records",
            "documents",
            "processes",
            "clients",
            "tenant_users",
            "specialties",
            "users",
            "tenants",
            "super_admins"
        ]
        
        for table in tables_to_clear:
            try:
                db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
                print(f"   ✅ Tabela {table} limpa")
            except Exception as e:
                print(f"   ⚠️  Erro ao limpar {table}: {e}")
        
        # Reabilitar constraints
        print("   🔧 Reabilitando constraints...")
        db.execute(text("SET session_replication_role = DEFAULT;"))
        
        db.commit()
        print("✅ Base de dados limpa com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar base de dados: {e}")
        db.rollback()
    finally:
        db.close()

def create_super_admin():
    """Cria o super administrador com as credenciais especificadas"""
    db = SessionLocal()
    
    try:
        print("👤 Criando Super Administrador...")
        
        # Criar super admin
        super_admin = SuperAdmin(
            id=uuid.uuid4(),
            name="Administrador do Sistema",
            email="admin@admin.com",
            password_hash=pwd_context.hash("123456"),
            is_active=True,
            permissions={
                "manage_tenants": True,
                "manage_users": True,
                "view_analytics": True,
                "system_config": True,
                "backup_restore": True,
                "security_audit": True
            },
            created_at=datetime.now()
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print(f"✅ Super Administrador criado com sucesso!")
        print(f"   📧 Email: {super_admin.email}")
        print(f"   🔑 Senha: 123456")
        print(f"   🆔 ID: {super_admin.id}")
        
        return super_admin
        
    except Exception as e:
        print(f"❌ Erro ao criar Super Administrador: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def verify_database_state():
    """Verifica o estado final da base de dados"""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verificando estado da base de dados...")
        
        # Contar registros em cada tabela
        tables_to_check = [
            "super_admins",
            "tenants",
            "users",
            "tenant_users",
            "clients",
            "processes",
            "documents",
            "financial_records",
            "notifications",
            "audit_logs",
            "specialties",
            "temporary_permissions"
        ]
        
        for table_name in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                status = "✅" if result == 0 else "⚠️"
                print(f"   {status} {table_name}: {result} registros")
            except Exception as e:
                print(f"   ❌ {table_name}: Erro ao verificar - {e}")
        
        # Verificar se o super admin existe
        try:
            result = db.execute(text("SELECT email FROM super_admins LIMIT 1")).scalar()
            if result:
                print(f"   ✅ Super Admin: {result}")
            else:
                print(f"   ❌ Super Admin: Não encontrado")
        except Exception as e:
            print(f"   ❌ Erro ao verificar Super Admin: {e}")
        
        print("✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    finally:
        db.close()

def main():
    """Função principal"""
    print("🧹 LIMPEZA COMPLETA DA BASE DE DADOS (FORÇADA)")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Esta operação irá apagar TODOS os dados!")
    print("   Apenas o Super Administrador será mantido.")
    print("   Este método é mais agressivo e pode quebrar constraints.")
    print("=" * 60)
    
    # Confirmar a operação
    confirm = input("\n🤔 Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
    if confirm != "SIM":
        print("❌ Operação cancelada!")
        return
    
    print("\n🚀 Iniciando limpeza forçada...")
    
    # 1. Limpar toda a base de dados
    clear_database_force()
    
    # 2. Criar super administrador
    super_admin = create_super_admin()
    
    # 3. Verificar estado final
    verify_database_state()
    
    print("\n" + "=" * 60)
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("\n📋 Resumo:")
    print("   - Todas as tabelas foram limpas")
    print("   - Super Administrador criado")
    print("   - Base de dados pronta para uso")
    print("\n🔑 Credenciais do Super Admin:")
    print("   📧 Email: admin@admin.com")
    print("   🔑 Senha: 123456")
    print("\n🔗 URL de acesso:")
    print("   http://localhost:3000/superadmin/login")
    print("\n💡 Agora você pode cadastrar tudo do zero!")

if __name__ == "__main__":
    main()
