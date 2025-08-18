from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import get_db
from core.auth.permission_system import require_permission
from core.services.cnj_integration import CNJIntegrationService
from apps.processes.schemas import ProcessResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cnj", tags=["Integração CNJ"])

@router.post("/consultar/{numero_cnj}")
async def consultar_processo_cnj(
    numero_cnj: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Consulta processo na API oficial do CNJ"""
    try:
        tenant_id = current_user_data["tenant"].id
        cnj_service = CNJIntegrationService(db)
        
        # Consultar dados na API CNJ
        dados_cnj = cnj_service.consultar_processo(numero_cnj)
        dados_processados = cnj_service.processar_dados_processo(dados_cnj)
        
        return {
            "success": True,
            "data": dados_processados,
            "message": "Processo encontrado na API CNJ"
        }
        
    except Exception as e:
        logger.error(f"Erro ao consultar processo CNJ {numero_cnj}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao consultar processo: {str(e)}"
        )

@router.post("/importar/{numero_cnj}")
async def importar_processo_cnj(
    numero_cnj: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "create"))
):
    """Importa processo automaticamente da API CNJ"""
    try:
        tenant_id = current_user_data["tenant"].id
        user_id = current_user_data["user"].id
        
        cnj_service = CNJIntegrationService(db)
        
        # Criar processo automaticamente
        processo = cnj_service.criar_processo_automatico(numero_cnj, str(tenant_id), str(user_id))
        
        # Adicionar tarefa em background para sincronização contínua
        background_tasks.add_task(
            cnj_service.atualizar_processo_existente,
            str(processo.id),
            numero_cnj
        )
        
        return {
            "success": True,
            "process_id": str(processo.id),
            "message": "Processo importado com sucesso da API CNJ"
        }
        
    except Exception as e:
        logger.error(f"Erro ao importar processo CNJ {numero_cnj}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao importar processo: {str(e)}"
        )

@router.put("/sincronizar/{process_id}")
async def sincronizar_processo_cnj(
    process_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Sincroniza processo existente com dados da API CNJ"""
    try:
        tenant_id = current_user_data["tenant"].id
        
        # Buscar processo
        from core.models.process import Process
        processo = db.query(Process).filter(
            Process.id == process_id,
            Process.tenant_id == tenant_id
        ).first()
        
        if not processo:
            raise HTTPException(status_code=404, detail="Processo não encontrado")
        
        if not processo.cnj_number:
            raise HTTPException(
                status_code=400, 
                detail="Processo não possui número CNJ para sincronização"
            )
        
        cnj_service = CNJIntegrationService(db)
        
        # Sincronizar em background
        background_tasks.add_task(
            cnj_service.atualizar_processo_existente,
            process_id,
            processo.cnj_number
        )
        
        return {
            "success": True,
            "message": "Sincronização iniciada em background"
        }
        
    except Exception as e:
        logger.error(f"Erro ao sincronizar processo {process_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao sincronizar processo: {str(e)}"
        )

@router.get("/processos-similares/{numero_cnj}")
async def buscar_processos_similares(
    numero_cnj: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Busca processos similares no sistema"""
    try:
        tenant_id = current_user_data["tenant"].id
        cnj_service = CNJIntegrationService(db)
        
        processos_similares = cnj_service.buscar_processos_similares(numero_cnj, str(tenant_id))
        
        return {
            "success": True,
            "processos": [
                {
                    "id": str(p.id),
                    "cnj_number": p.cnj_number,
                    "subject": p.subject,
                    "court": p.court,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                }
                for p in processos_similares
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar processos similares: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar processos similares: {str(e)}"
        )

@router.get("/status/{numero_cnj}")
async def verificar_status_processo_cnj(
    numero_cnj: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Verifica se processo existe na API CNJ e retorna status"""
    try:
        cnj_service = CNJIntegrationService(db)
        
        # Tentar consultar processo
        dados_cnj = cnj_service.consultar_processo(numero_cnj)
        dados_processados = cnj_service.processar_dados_processo(dados_cnj)
        
        return {
            "success": True,
            "exists": True,
            "status": dados_processados.get('status'),
            "last_update": dados_processados.get('ultima_atualizacao'),
            "court": dados_processados.get('tribunal'),
            "subject": dados_processados.get('assunto')
        }
        
    except Exception as e:
        return {
            "success": True,
            "exists": False,
            "error": str(e)
        }

@router.post("/validar-cnj/{numero_cnj}")
async def validar_numero_cnj(
    numero_cnj: str,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Valida formato do número CNJ e identifica tribunal"""
    try:
        cnj_service = CNJIntegrationService(db)
        
        # Extrair informações do tribunal
        alias, url = cnj_service.extrair_tribunal(numero_cnj)
        
        # Limpar número
        import re
        numero_limpo = re.sub(r'\D', '', numero_cnj)
        
        # Extrair componentes
        sequencial = numero_limpo[:7]
        dv = numero_limpo[7:9]
        ano = numero_limpo[9:13]
        justica = numero_limpo[13]
        tribunal = numero_limpo[14:16]
        vara = numero_limpo[16:20]
        
        return {
            "success": True,
            "valid": True,
            "tribunal": {
                "alias": alias,
                "url": url,
                "nome": f"Tribunal {alias.upper()}"
            },
            "componentes": {
                "sequencial": sequencial,
                "dv": dv,
                "ano": ano,
                "justica": justica,
                "tribunal": tribunal,
                "vara": vara
            },
            "numero_formatado": f"{sequencial}-{dv}.{ano}.{justica}.{tribunal}.{vara}"
        }
        
    except Exception as e:
        return {
            "success": True,
            "valid": False,
            "error": str(e)
        }

@router.get("/stats")
async def get_cnj_stats(
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "read"))
):
    """Retorna estatísticas da integração CNJ"""
    try:
        tenant_id = current_user_data["tenant"].id
        logger.info(f"Buscando estatísticas CNJ para tenant: {tenant_id}")
        
        # Buscar processos do tenant
        from core.models.process import Process
        from sqlalchemy import and_
        
        # Total de processos
        total_processos = db.query(Process).filter(
            Process.tenant_id == tenant_id
        ).count()
        logger.info(f"Total de processos: {total_processos}")
        
        # Processos com número CNJ
        processos_com_cnj = db.query(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                Process.cnj_number.isnot(None),
                Process.cnj_number != ""
            )
        ).count()
        logger.info(f"Processos com CNJ: {processos_com_cnj}")
        
        # Processos sem número CNJ
        processos_sem_cnj = total_processos - processos_com_cnj
        
        # Calcular taxa de sucesso (assumindo que processos com CNJ são sincronizados)
        taxa_sucesso = (processos_com_cnj / total_processos * 100) if total_processos > 0 else 0
        
        # Última sincronização (buscar processo mais recente com CNJ)
        ultimo_processo_cnj = db.query(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                Process.cnj_number.isnot(None),
                Process.cnj_number != ""
            )
        ).order_by(Process.updated_at.desc()).first()
        
        ultima_sincronizacao = ultimo_processo_cnj.updated_at.isoformat() if ultimo_processo_cnj and ultimo_processo_cnj.updated_at else None
        
        return {
            "total_processos": total_processos,
            "processos_sincronizados": processos_com_cnj,
            "processos_pendentes": processos_sem_cnj,
            "ultima_sincronizacao": ultima_sincronizacao,
            "taxa_sucesso": round(taxa_sucesso, 2)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas CNJ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )

@router.post("/sync-all")
async def sincronizar_todos_processos_cnj(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user_data: dict = Depends(require_permission("processes", "update"))
):
    """Sincroniza todos os processos com número CNJ"""
    try:
        tenant_id = current_user_data["tenant"].id
        
        # Buscar todos os processos com CNJ
        from core.models.process import Process
        from sqlalchemy import and_
        
        processos_com_cnj = db.query(Process).filter(
            and_(
                Process.tenant_id == tenant_id,
                Process.cnj_number.isnot(None),
                Process.cnj_number != ""
            )
        ).all()
        
        if not processos_com_cnj:
            return {
                "success": True,
                "message": "Nenhum processo com número CNJ encontrado para sincronização",
                "processos_sincronizados": 0
            }
        
        cnj_service = CNJIntegrationService(db)
        
        # Adicionar tarefas em background para cada processo
        for processo in processos_com_cnj:
            background_tasks.add_task(
                cnj_service.atualizar_processo_existente,
                str(processo.id),
                processo.cnj_number
            )
        
        return {
            "success": True,
            "message": f"Sincronização em massa iniciada para {len(processos_com_cnj)} processos",
            "processos_sincronizados": len(processos_com_cnj)
        }
        
    except Exception as e:
        logger.error(f"Erro ao sincronizar todos os processos CNJ: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sincronizar processos: {str(e)}"
        )
