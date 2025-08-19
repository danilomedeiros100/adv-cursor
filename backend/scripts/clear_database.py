#!/usr/bin/env python3
"""
Script para limpar toda a base de dados e deixar apenas o super administrador
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import SessionLocal, engine
from core.models.superadmin import SuperAdmin
from core.models.tenant import Tenant
from core.models.user import User
from core.models.tenant_user import TenantUser
from core.models.client import Client
from core.models.process import Process
from core.models.document import Document
from core.models.financial import FinancialRecord
from core.models.notification import ProcessNotification
from core.models.audit import AuditLog
from core.models.specialty import Specialty
from core.models.temporary_permissions import TemporaryPermission
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def clear_all_tables():
    """Limpa todas as tabelas da base de dados"""
    db = SessionLocal()
    
    try:
        print("🗑️  Limpando todas as tabelas...")
        
        # Lista de todas as tabelas para limpar (em ordem de dependência)
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
            "superadmins"
        ]
        
        for table in tables_to_clear:
            try:
                # Usar SQL direto para garantir que a tabela seja limpa
                db.execute(text(f"DELETE FROM {table}"))
                print(f"   ✅ Tabela {table} limpa")
            except Exception as e:
                print(f"   ⚠️  Erro ao limpar {table}: {e}")
        
        db.commit()
        print("✅ Todas as tabelas foram limpas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar tabelas: {e}")
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
            created_at=datetime.utcnow()
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
            ("superadmins", SuperAdmin),
            ("tenants", Tenant),
            ("users", User),
            ("tenant_users", TenantUser),
            ("clients", Client),
            ("processes", Process),
            ("documents", Document),
            ("financial_records", FinancialRecord),
            ("notifications", ProcessNotification),
            ("audit_logs", AuditLog),
            ("specialties", Specialty),
            ("temporary_permissions", TemporaryPermission)
        ]
        
        for table_name, model in tables_to_check:
            count = db.query(model).count()
            status = "✅" if count == 0 else "⚠️"
            print(f"   {status} {table_name}: {count} registros")
        
        # Verificar se o super admin existe
        super_admin = db.query(SuperAdmin).first()
        if super_admin:
            print(f"   ✅ Super Admin: {super_admin.email}")
        else:
            print(f"   ❌ Super Admin: Não encontrado")
        
        print("✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    finally:
        db.close()

def main():
    """Função principal"""
    print("🧹 LIMPEZA COMPLETA DA BASE DE DADOS")
    print("=" * 50)
    print("⚠️  ATENÇÃO: Esta operação irá apagar TODOS os dados!")
    print("   Apenas o Super Administrador será mantido.")
    print("=" * 50)
    
    # Confirmar a operação
    confirm = input("\n🤔 Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
    if confirm != "SIM":
        print("❌ Operação cancelada!")
        return
    
    print("\n🚀 Iniciando limpeza...")
    
    # 1. Limpar todas as tabelas
    clear_all_tables()
    
    # 2. Criar super administrador
    super_admin = create_super_admin()
    
    # 3. Verificar estado final
    verify_database_state()
    
    print("\n" + "=" * 50)
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
