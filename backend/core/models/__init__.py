# Importar todos os modelos para garantir que sejam registrados
from .tenant import Tenant
from .user import User
from .tenant_user import TenantUser
from .client import Client
from .process import Process
from .document import DocumentTemplate
from .financial import FinancialRecord, FeeStructure
from .notification import Notification, NotificationTemplate
from .audit import AuditLog, DataAccessLog, SecurityEvent
from .superadmin import SuperAdmin
from .user_roles import UserSpecialty, LegalSpecialty
from .specialty import Specialty
from .temporary_permissions import TemporaryPermission

__all__ = [
    'Tenant',
    'User', 
    'TenantUser',
    'Client',
    'Process',
    'DocumentTemplate',
    'FinancialRecord',
    'FeeStructure',
    'Notification',
    'NotificationTemplate',
    'AuditLog',
    'DataAccessLog',
    'SecurityEvent',
    'SuperAdmin',
    'UserSpecialty',
    'LegalSpecialty',
    'Specialty',
    'TemporaryPermission'
]
