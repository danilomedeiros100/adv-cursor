from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Importações dos módulos
from core.database import engine, Base
from core.middleware.tenant_isolation import TenantIsolationMiddleware

# Rotas Super Admin
from apps.superadmin.routes import router as superadmin_router
from apps.superadmin.dashboard.routes import router as superadmin_dashboard_router

# Rotas Empresas
from apps.company.dashboard.routes import router as company_dashboard_router
from apps.clients import router as clients_router
from apps.processes import router as processes_router
from apps.users import router as users_router
from apps.specialties import router as specialties_router
# from apps.documents.routes import router as documents_router
# from apps.financial.routes import router as financial_router
# from apps.notifications.routes import router as notifications_router

# Rotas Portal Cliente
# from apps.client_portal.routes import router as client_portal_router

# Rotas Auth
from apps.auth.routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle da aplicação"""
    # Startup
    print("🚀 Iniciando SaaS Jurídico...")
    
    # Cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    print("🛑 Encerrando SaaS Jurídico...")

# Criação da aplicação
app = FastAPI(
    title="SaaS Jurídico",
    description="Sistema multi-tenant para escritórios de advocacia",
    version="1.0.0",
    lifespan=lifespan
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configurar em produção
)

app.add_middleware(TenantIsolationMiddleware)

# Rotas Super Admin (Portal de Gestão do SaaS)
app.include_router(
    superadmin_router,
    prefix="/api/v1/superadmin",
    tags=["Super Admin"]
)

app.include_router(
    superadmin_dashboard_router,
    prefix="/api/v1/superadmin",
    tags=["Super Admin Dashboard"]
)

# Rotas Empresas (Portal Operacional)
app.include_router(
    company_dashboard_router,
    prefix="/api/v1/company",
    tags=["Company Dashboard"]
)

app.include_router(
    clients_router,
    prefix="/api/v1/company",
    tags=["Clients"]
)

app.include_router(
    processes_router,
    prefix="/api/v1/company",
    tags=["Processes"]
)

app.include_router(
    users_router,
    prefix="/api/v1/company",
    tags=["Users"]
)

app.include_router(
    specialties_router,
    prefix="/api/v1/company",
    tags=["Specialties"]
)

# app.include_router(
#     documents_router,
#     prefix="/api/v1/company",
#     tags=["Documents"]
# )

# app.include_router(
#     financial_router,
#     prefix="/api/v1/company",
#     tags=["Financial"]
# )

# app.include_router(
#     notifications_router,
#     prefix="/api/v1/company",
#     tags=["Notifications"]
# )

# Rotas Portal Cliente (Acesso Externo)
# app.include_router(
#     client_portal_router,
#     prefix="/api/v1/client",
#     tags=["Client Portal"]
# )

# Rotas de Autenticação
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "SaaS Jurídico API",
        "version": "1.0.0",
        "status": "running",
        "portals": {
            "superadmin": "/api/v1/superadmin",
            "company": "/api/v1/company",
            "client": "/api/v1/client"
        }
    }

@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "elasticsearch": "connected"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
