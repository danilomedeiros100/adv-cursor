#!/usr/bin/env python3
"""
Script para criar dados iniciais do sistema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.models.tenant import Tenant
from core.models.user import User, UserProfile
from core.models.user_roles import Role
from core.models.tenant_user import TenantUser
from core.models.specialty import Specialty
from core.models.superadmin import SuperAdmin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import uuid

def create_seed_data():
    """Criar dados iniciais do sistema"""
    db = SessionLocal()
    
    try:
        print("🌱 Criando dados iniciais...")
        
        # 1. Criar Super Admin
        print("1. Criando Super Admin...")
        super_admin = SuperAdmin(
            id=uuid.uuid4(),
            name="Super Administrador",
            email="admin@saasjuridico.com",
            password_hash=pwd_context.hash("admin123"),
            is_active=True
        )
        db.add(super_admin)
        db.flush()
        
        # 2. Criar Roles padrão
        print("2. Criando Roles padrão...")
        roles = {
            "admin": Role(
                id=uuid.uuid4(),
                name="admin",
                display_name="Administrador",
                description="Administrador da empresa",
                default_permissions={
                    "users.manage": True,
                    "financial.manage": True,
                    "processes.view_all": True,
                    "specialties.manage": True
                },
                can_manage_users=True,
                can_manage_financial=True,
                can_view_all_processes=True,
                can_manage_specialties=True
            ),
            "lawyer": Role(
                id=uuid.uuid4(),
                name="lawyer",
                display_name="Advogado",
                description="Advogado da empresa",
                default_permissions={
                    "processes.create": True,
                    "processes.read": True,
                    "processes.update": True,
                    "clients.create": True,
                    "clients.read": True,
                    "clients.update": True,
                    "documents.create": True,
                    "documents.read": True
                },
                can_manage_users=False,
                can_manage_financial=False,
                can_view_all_processes=False,
                can_manage_specialties=False
            ),
            "assistant": Role(
                id=uuid.uuid4(),
                name="assistant",
                display_name="Assistente",
                description="Assistente jurídico",
                default_permissions={
                    "processes.read": True,
                    "clients.read": True,
                    "documents.read": True
                },
                can_manage_users=False,
                can_manage_financial=False,
                can_view_all_processes=False,
                can_manage_specialties=False
            )
        }
        
        for role in roles.values():
            db.add(role)
        db.flush()
        
        # 3. Criar Tenant demo
        print("3. Criando Tenant demo...")
        demo_tenant = Tenant(
            id=uuid.uuid4(),
            name="Escritório Demo",
            slug="demo",
            email="contato@escritoriodemo.com",
            phone="(11) 99999-9999",
            plan_type="premium",
            plan_features={
                "max_users": 50,
                "max_processes": 1000,
                "modules": ["clients", "processes", "documents", "financial", "notifications"]
            },
            max_users=50,
            max_processes=1000,
            is_active=True,
            is_suspended=False,
            settings={
                "timezone": "America/Sao_Paulo",
                "language": "pt_BR",
                "currency": "BRL"
            },
            branding={
                "logo_url": None,
                "primary_color": "#3B82F6",
                "company_name": "Escritório Demo"
            }
        )
        db.add(demo_tenant)
        db.flush()
        
        # 4. Criar usuário admin da empresa
        print("4. Criando usuário admin da empresa...")
        admin_user = User(
            id=uuid.uuid4(),
            name="João Silva",
            email="joao@escritoriodemo.com",
            password_hash=pwd_context.hash("123456"),
            phone="(11) 88888-8888",
            oab_number="123456",
            oab_state="SP",
            position="Sócio",
            department="Administrativo",
            is_active=True,
            is_super_admin=False,
            email_verified=True,
            phone_verified=True,
            preferences={
                "theme": "light",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            timezone="America/Sao_Paulo",
            language="pt_BR"
        )
        db.add(admin_user)
        db.flush()
        
        # 5. Criar perfil do usuário
        admin_profile = UserProfile(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            bio="Advogado especialista em direito civil e empresarial",
            experience_years=10,
            education=[
                {"degree": "Bacharel em Direito", "institution": "USP", "year": 2010},
                {"degree": "Especialização em Direito Civil", "institution": "PUC-SP", "year": 2012}
            ],
            certifications=[
                {"name": "OAB/SP", "number": "123456", "year": 2011}
            ],
            address={
                "street": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01234-567",
                "country": "Brasil"
            },
            emergency_contact={
                "name": "Maria Silva",
                "phone": "(11) 77777-7777",
                "relationship": "Esposa"
            },
            working_hours={
                "monday": {"start": "09:00", "end": "18:00"},
                "tuesday": {"start": "09:00", "end": "18:00"},
                "wednesday": {"start": "09:00", "end": "18:00"},
                "thursday": {"start": "09:00", "end": "18:00"},
                "friday": {"start": "09:00", "end": "18:00"}
            },
            availability={
                "weekdays": True,
                "weekends": False,
                "holidays": False
            }
        )
        db.add(admin_profile)
        
        # 6. Associar usuário ao tenant
        tenant_user = TenantUser(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            user_id=admin_user.id,
            role="admin",
            permissions={
                "users.manage": True,
                "financial.manage": True,
                "processes.view_all": True,
                "specialties.manage": True
            },
            department="Administrativo",
            position="Sócio",
            is_active=True,
            is_primary_admin=True
        )
        db.add(tenant_user)
        
        # 7. Criar especialidades jurídicas
        print("5. Criando especialidades jurídicas...")
        specialties = [
            Specialty(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                name="Direito Civil",
                code="CIVIL",
                description="Direito Civil e Contratual",
                is_active=True,
                requires_oab=True,
                color="#3B82F6",
                icon="scale",
                display_order="1"
            ),
            Specialty(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                name="Direito Trabalhista",
                code="TRABALHISTA",
                description="Direito do Trabalho",
                is_active=True,
                requires_oab=True,
                color="#EF4444",
                icon="briefcase",
                display_order="2"
            ),
            Specialty(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                name="Direito Empresarial",
                code="EMPRESARIAL",
                description="Direito Empresarial e Societário",
                is_active=True,
                requires_oab=True,
                color="#10B981",
                icon="building",
                display_order="3"
            )
        ]
        
        for specialty in specialties:
            db.add(specialty)
        
        # 8. Criar usuário advogado
        print("6. Criando usuário advogado...")
        lawyer_user = User(
            id=uuid.uuid4(),
            name="Maria Santos",
            email="maria@escritoriodemo.com",
            password_hash=pwd_context.hash("123456"),
            phone="(11) 77777-7777",
            oab_number="654321",
            oab_state="SP",
            position="Advogada",
            department="Civil",
            is_active=True,
            is_super_admin=False,
            email_verified=True,
            phone_verified=True,
            preferences={
                "theme": "light",
                "notifications": {
                    "email": True,
                    "push": True,
                    "sms": False
                }
            },
            timezone="America/Sao_Paulo",
            language="pt_BR"
        )
        db.add(lawyer_user)
        db.flush()
        
        # 9. Associar advogada ao tenant
        lawyer_tenant_user = TenantUser(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            user_id=lawyer_user.id,
            role="lawyer",
            permissions={
                "processes.create": True,
                "processes.read": True,
                "processes.update": True,
                "clients.create": True,
                "clients.read": True,
                "clients.update": True
            },
            department="Civil",
            position="Advogada",
            is_active=True,
            is_primary_admin=False
        )
        db.add(lawyer_tenant_user)
        
        # Commit das alterações
        db.commit()
        
        print("✅ Dados iniciais criados com sucesso!")
        print("\n📋 Credenciais de acesso:")
        print("=" * 50)
        print("🔐 Super Admin:")
        print("   Email: admin@saasjuridico.com")
        print("   Senha: admin123")
        print()
        print("🏢 Empresa Demo:")
        print("   Email: joao@escritoriodemo.com")
        print("   Senha: 123456")
        print("   Tenant: demo")
        print()
        print("👩‍💼 Advogada:")
        print("   Email: maria@escritoriodemo.com")
        print("   Senha: 123456")
        print("   Tenant: demo")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar dados iniciais: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
