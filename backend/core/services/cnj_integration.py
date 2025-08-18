import re
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from core.models.process import Process, ProcessTimeline
from core.models.client import Client
from core.models.user import User
import uuid

logger = logging.getLogger(__name__)

class CNJIntegrationService:
    """Serviço para integração com a API oficial do CNJ (DataJud)"""
    
    # Mapeamento dos tribunais por grau.estado
    TRIBUNAIS_MAPA = {
        # Justiça Estadual (TJ)
        '8.01': 'tjac',   # Acre
        '8.02': 'tjal',   # Alagoas
        '8.03': 'tjam',   # Amazonas
        '8.04': 'tjap',   # Amapá
        '8.05': 'tjba',   # Bahia
        '8.06': 'tjce',   # Ceará
        '8.07': 'tjdft',  # Distrito Federal e Territórios
        '8.08': 'tjes',   # Espírito Santo
        '8.09': 'tjgo',   # Goiás
        '8.10': 'tjma',   # Maranhão
        '8.11': 'tjmg',   # Minas Gerais
        '8.12': 'tjms',   # Mato Grosso do Sul
        '8.13': 'tjmt',   # Mato Grosso
        '8.14': 'tjpa',   # Pará
        '8.15': 'tjpb',   # Paraíba
        '8.16': 'tjpr',   # Paraná
        '8.17': 'tjpe',   # Pernambuco
        '8.18': 'tjpi',   # Piauí
        '8.19': 'tjrj',   # Rio de Janeiro
        '8.20': 'tjrn',   # Rio Grande do Norte
        '8.21': 'tjro',   # Rondônia
        '8.22': 'tjrr',   # Roraima
        '8.23': 'tjrs',   # Rio Grande do Sul
        '8.24': 'tjsc',   # Santa Catarina
        '8.25': 'tjse',   # Sergipe
        '8.26': 'tjsp',   # São Paulo
        '8.27': 'tjto',   # Tocantins

        # Justiça Federal (TRF)
        '5.01': 'trf1',
        '5.02': 'trf2',
        '5.03': 'trf3',
        '5.04': 'trf4',
        '5.05': 'trf5',
        '5.06': 'trf6',

        # Manutenção compatibilidade (grau isolado)
        '1': 'trf1',
        '2': 'trf2',
        '3': 'trf3',
        '4': 'trf4',
        '5': 'trf5',
        '6': 'trf6',

        # Justiça Eleitoral (exemplos)
        '42': 'tre-al',
        '43': 'tre-ba',
        '44': 'tre-sp',

        # Justiça do Trabalho (exemplo)
        '21': 'trt21',

        # Tribunais Superiores fixos
        'tst': 'tst',
        'tse': 'tse',
        'stj': 'stj',
        'stm': 'stm',
    }
    
    def __init__(self, db: Session, api_key: str = None):
        self.db = db
        self.api_key = api_key or "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
        self.base_url = "https://api-publica.datajud.cnj.jus.br"
    
    def extrair_tribunal(self, numero_processo: str) -> tuple[str, str]:
        """Extrai informações do tribunal a partir do número do processo"""
        numero_limpo = re.sub(r'\D', '', numero_processo)
        
        if len(numero_limpo) != 20:
            raise ValueError(f"Número do processo '{numero_processo}' inválido: deve conter 20 dígitos.")

        sequencial = numero_limpo[:7]
        dv = numero_limpo[7:9]
        ano = numero_limpo[9:13]
        justica = numero_limpo[13]       # Justiça
        tribunal = numero_limpo[14:16]   # Tribunal (TRF1, TRF2...)
        vara = numero_limpo[16:20]

        logger.debug(f"DEBUG: sequencial={sequencial}, dv={dv}, ano={ano}, justica={justica}, tribunal={tribunal}, vara={vara}")

        chave = f"{justica}.{tribunal}"

        # Tratamento especial para TRF1 com codificação antiga
        if justica == '4' and tribunal == '01':
            chave = '5.01'

        alias = self.TRIBUNAIS_MAPA.get(chave)
        if not alias:
            alias = self.TRIBUNAIS_MAPA.get(justica)
        if not alias:
            raise ValueError(f"Tribunal não encontrado para o código '{chave}'.")

        url = f"{self.base_url}/api_publica_{alias}/_search"
        return alias, url
    
    def consultar_processo(self, numero_processo: str) -> Dict[str, Any]:
        """Consulta o processo na API DataJud e retorna os dados"""
        try:
            _, url = self.extrair_tribunal(numero_processo)
            numero_limpo = re.sub(r'\D', '', numero_processo)

            payload = {
                "query": {
                    "match": {
                        "numeroProcesso": numero_limpo
                    }
                }
            }

            headers = {
                'Authorization': f'ApiKey {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao consultar processo {numero_processo}: {e}")
            raise
    
    def processar_dados_processo(self, dados_cnj: Dict[str, Any]) -> Dict[str, Any]:
        """Processa e estrutura os dados retornados pela API CNJ"""
        try:
            # Extrair dados básicos do processo
            hits = dados_cnj.get('hits', {}).get('hits', [])
            if not hits:
                raise ValueError("Processo não encontrado na API CNJ")
            
            source = hits[0].get('_source', {})
            
            # Estruturar dados processados
            dados_processados = {
                'numero_processo': source.get('numeroProcesso'),
                'classe_processual': source.get('classeProcessual'),
                'assunto': source.get('assunto'),
                'data_distribuicao': source.get('dataDistribuicao'),
                'orgao_julgador': source.get('orgaoJulgador'),
                'tribunal': source.get('tribunal'),
                'vara': source.get('vara'),
                'valor_causa': source.get('valorCausa'),
                'partes': source.get('partes', []),
                'andamentos': source.get('movimentos', []),
                'documentos': source.get('documentos', []),
                'status': source.get('status'),
                'ultima_atualizacao': source.get('ultimaAtualizacao')
            }
            
            return dados_processados
            
        except Exception as e:
            logger.error(f"Erro ao processar dados do processo: {e}")
            raise
    
    def criar_processo_automatico(self, numero_cnj: str, tenant_id: str, created_by: str) -> Process:
        """Cria processo automaticamente a partir do número CNJ"""
        try:
            # Consultar dados na API CNJ
            dados_cnj = self.consultar_processo(numero_cnj)
            dados_processados = self.processar_dados_processo(dados_cnj)
            
            # Criar ou encontrar cliente
            cliente = self._criar_ou_encontrar_cliente(dados_processados, tenant_id)
            
            # Criar processo
            processo = Process(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                cnj_number=numero_cnj,
                subject=dados_processados.get('assunto', 'Processo importado do CNJ'),
                court=dados_processados.get('tribunal'),
                jurisdiction=dados_processados.get('orgaoJulgador'),
                client_id=cliente.id,
                status='active',
                priority='normal',
                estimated_value=self._extrair_valor_causa(dados_processados.get('valorCausa')),
                notes=f"Processo importado automaticamente do CNJ em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                created_by=created_by
            )
            
            self.db.add(processo)
            self.db.flush()
            
            # Criar timeline de andamentos
            self._criar_timeline_andamentos(processo.id, dados_processados.get('andamentos', []), created_by)
            
            self.db.commit()
            return processo
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar processo automático: {e}")
            raise
    
    def atualizar_processo_existente(self, processo_id: str, numero_cnj: str) -> bool:
        """Atualiza processo existente com dados da API CNJ"""
        try:
            # Buscar processo existente
            processo = self.db.query(Process).filter(Process.id == processo_id).first()
            if not processo:
                raise ValueError("Processo não encontrado")
            
            # Consultar dados atualizados
            dados_cnj = self.consultar_processo(numero_cnj)
            dados_processados = self.processar_dados_processo(dados_cnj)
            
            # Atualizar dados básicos
            processo.subject = dados_processados.get('assunto', processo.subject)
            processo.court = dados_processados.get('tribunal', processo.court)
            processo.jurisdiction = dados_processados.get('orgaoJulgador', processo.jurisdiction)
            processo.estimated_value = self._extrair_valor_causa(dados_processados.get('valorCausa'))
            processo.updated_at = datetime.now()
            
            # Atualizar timeline
            self._atualizar_timeline_andamentos(processo_id, dados_processados.get('andamentos', []))
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar processo: {e}")
            raise
    
    def _criar_ou_encontrar_cliente(self, dados_processo: Dict[str, Any], tenant_id: str) -> Client:
        """Cria ou encontra cliente baseado nos dados do processo"""
        # Extrair informações das partes
        partes = dados_processo.get('partes', [])
        parte_principal = None
        
        for parte in partes:
            if parte.get('tipo') == 'REQUERENTE' or parte.get('tipo') == 'AUTOR':
                parte_principal = parte
                break
        
        if not parte_principal:
            # Criar cliente genérico
            cliente = Client(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                name="Cliente Importado do CNJ",
                person_type="PF",
                is_active=True
            )
        else:
            # Criar cliente com dados da parte
            nome = parte_principal.get('nome', 'Cliente Importado do CNJ')
            documento = parte_principal.get('documento')
            
            cliente = Client(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                name=nome,
                cpf_cnpj=documento,
                person_type="PJ" if documento and len(documento) > 11 else "PF",
                is_active=True
            )
        
        self.db.add(cliente)
        self.db.flush()
        return cliente
    
    def _extrair_valor_causa(self, valor_causa: str) -> Optional[int]:
        """Extrai valor da causa em centavos"""
        if not valor_causa:
            return None
        
        try:
            # Remover caracteres não numéricos e converter para centavos
            valor_limpo = re.sub(r'[^\d,.]', '', valor_causa)
            valor_float = float(valor_limpo.replace(',', '.'))
            return int(valor_float * 100)  # Converter para centavos
        except:
            return None
    
    def _criar_timeline_andamentos(self, processo_id: str, andamentos: List[Dict], created_by: str):
        """Cria timeline de andamentos a partir dos dados do CNJ"""
        for andamento in andamentos:
            try:
                data_andamento = datetime.fromisoformat(andamento.get('data', '').replace('Z', '+00:00'))
                
                timeline_entry = ProcessTimeline(
                    id=uuid.uuid4(),
                    process_id=processo_id,
                    date=data_andamento,
                    type=andamento.get('tipo', 'andamento'),
                    description=andamento.get('descricao', ''),
                    court_decision=andamento.get('decisao'),
                    ai_classification=self._classificar_andamento(andamento.get('descricao', '')),
                    created_by=created_by
                )
                
                self.db.add(timeline_entry)
                
            except Exception as e:
                logger.warning(f"Erro ao criar andamento: {e}")
                continue
    
    def _atualizar_timeline_andamentos(self, processo_id: str, andamentos: List[Dict]):
        """Atualiza timeline com novos andamentos"""
        # Buscar andamentos existentes
        andamentos_existentes = self.db.query(ProcessTimeline).filter(
            ProcessTimeline.process_id == processo_id
        ).all()
        
        # Criar set de datas existentes para evitar duplicatas
        datas_existentes = {a.date.isoformat() for a in andamentos_existentes}
        
        # Adicionar apenas andamentos novos
        for andamento in andamentos:
            try:
                data_andamento = datetime.fromisoformat(andamento.get('data', '').replace('Z', '+00:00'))
                
                if data_andamento.isoformat() not in datas_existentes:
                    timeline_entry = ProcessTimeline(
                        id=uuid.uuid4(),
                        process_id=processo_id,
                        date=data_andamento,
                        type=andamento.get('tipo', 'andamento'),
                        description=andamento.get('descricao', ''),
                        court_decision=andamento.get('decisao'),
                        ai_classification=self._classificar_andamento(andamento.get('descricao', '')),
                        created_by=None  # Sistema
                    )
                    
                    self.db.add(timeline_entry)
                    
            except Exception as e:
                logger.warning(f"Erro ao atualizar andamento: {e}")
                continue
    
    def _classificar_andamento(self, descricao: str) -> str:
        """Classifica automaticamente o tipo de andamento"""
        descricao_lower = descricao.lower()
        
        if any(palavra in descricao_lower for palavra in ['sentença', 'decisão', 'julgamento']):
            return 'sentença'
        elif any(palavra in descricao_lower for palavra in ['audiência', 'sessão']):
            return 'audiência'
        elif any(palavra in descricao_lower for palavra in ['petição', 'requerimento']):
            return 'petição'
        elif any(palavra in descricao_lower for palavra in ['despacho', 'decisão interlocutória']):
            return 'despacho'
        elif any(palavra in descricao_lower for palavra in ['prazo', 'intimação']):
            return 'prazo'
        else:
            return 'andamento'
    
    def buscar_processos_similares(self, numero_cnj: str, tenant_id: str) -> List[Process]:
        """Busca processos similares no sistema"""
        try:
            # Extrair informações do número CNJ
            numero_limpo = re.sub(r'\D', '', numero_cnj)
            ano = numero_limpo[9:13]
            tribunal = numero_limpo[14:16]
            
            # Buscar processos do mesmo ano e tribunal
            processos_similares = self.db.query(Process).filter(
                Process.tenant_id == tenant_id,
                Process.cnj_number.like(f'%{ano}%'),
                Process.created_at >= datetime.now().replace(year=int(ano))
            ).limit(10).all()
            
            return processos_similares
            
        except Exception as e:
            logger.error(f"Erro ao buscar processos similares: {e}")
            return []
