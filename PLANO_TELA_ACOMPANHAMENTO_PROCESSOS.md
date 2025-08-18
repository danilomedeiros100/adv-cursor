# 📋 Plano de Implementação - Tela de Acompanhamento de Processos

## 🎯 Objetivo
Implementar uma tela completa de acompanhamento de processos com timeline, prazos, documentos e ações rápidas.

## 📊 Análise do Status Atual

### ✅ **O que já está implementado:**

#### **Backend - Modelos**
- ✅ **Process**: Modelo principal com informações básicas
- ✅ **ProcessTimeline**: Timeline de andamentos
- ✅ **ProcessDeadline**: Prazos críticos
- ✅ **ProcessLawyer**: Relacionamento com advogados
- ✅ **ProcessSpecialty**: Relacionamento com especialidades
- ✅ **Document**: Modelo para documentos
- ✅ **FinancialRecord**: Modelo para registros financeiros

#### **Backend - Endpoints**
- ✅ **GET /processes/{id}**: Obter processo específico
- ✅ **PUT /processes/{id}**: Atualizar processo
- ✅ **DELETE /processes/{id}**: Deletar processo

#### **Frontend - Estrutura**
- ✅ **Lista de processos**: Página principal
- ✅ **Formulário de criação**: Criar novo processo
- ✅ **Componente SearchableSelect**: Busca de entidades

### 🔄 **O que precisa ser implementado:**

## 🏗️ Implementação Backend

### **1. Endpoints para Timeline**
```python
# Novo endpoint para timeline
@router.get("/{process_id}/timeline")
async def get_process_timeline(process_id: str):
    """Obtém timeline de andamentos do processo"""

# Novo endpoint para adicionar andamento
@router.post("/{process_id}/timeline")
async def add_timeline_entry(process_id: str, entry_data: TimelineEntryCreate):
    """Adiciona novo andamento ao processo"""

# Novo endpoint para atualizar andamento
@router.put("/{process_id}/timeline/{entry_id}")
async def update_timeline_entry(process_id: str, entry_id: str, entry_data: TimelineEntryUpdate):
    """Atualiza andamento do processo"""
```

### **2. Endpoints para Prazos**
```python
# Novo endpoint para prazos
@router.get("/{process_id}/deadlines")
async def get_process_deadlines(process_id: str):
    """Obtém prazos do processo"""

# Novo endpoint para adicionar prazo
@router.post("/{process_id}/deadlines")
async def add_deadline(process_id: str, deadline_data: DeadlineCreate):
    """Adiciona novo prazo ao processo"""

# Novo endpoint para marcar prazo como concluído
@router.put("/{process_id}/deadlines/{deadline_id}/complete")
async def complete_deadline(process_id: str, deadline_id: str):
    """Marca prazo como concluído"""
```

### **3. Endpoints para Documentos**
```python
# Novo endpoint para documentos
@router.get("/{process_id}/documents")
async def get_process_documents(process_id: str):
    """Obtém documentos do processo"""

# Novo endpoint para upload de documento
@router.post("/{process_id}/documents")
async def upload_document(process_id: str, file: UploadFile):
    """Faz upload de documento para o processo"""

# Novo endpoint para download de documento
@router.get("/{process_id}/documents/{document_id}/download")
async def download_document(process_id: str, document_id: str):
    """Faz download de documento"""
```

### **4. Endpoints para Financeiro**
```python
# Novo endpoint para registros financeiros
@router.get("/{process_id}/financial")
async def get_process_financial(process_id: str):
    """Obtém registros financeiros do processo"""

# Novo endpoint para adicionar registro financeiro
@router.post("/{process_id}/financial")
async def add_financial_record(process_id: str, record_data: FinancialRecordCreate):
    """Adiciona registro financeiro ao processo"""
```

### **5. Schemas Atualizados**
```python
# Novos schemas para timeline
class TimelineEntryCreate(BaseModel):
    date: datetime
    type: str  # sentença, audiência, petição, etc.
    description: str
    court_decision: Optional[str] = None
    documents: Optional[List[str]] = []

class TimelineEntryUpdate(BaseModel):
    date: Optional[datetime] = None
    type: Optional[str] = None
    description: Optional[str] = None
    court_decision: Optional[str] = None

# Novos schemas para prazos
class DeadlineCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    deadline_type: str  # legal, internal, client
    notify_days_before: int = 3
    is_critical: bool = False

# Novos schemas para documentos
class DocumentCreate(BaseModel):
    name: str
    type: str  # petição, contrato, sentença, procuração
    description: Optional[str] = None
    file_path: str

# Novos schemas para financeiro
class FinancialRecordCreate(BaseModel):
    type: str  # honorários, custas, adiantamento
    amount: int  # Em centavos
    description: str
    due_date: Optional[datetime] = None
    status: str = "pending"  # pending, paid, overdue
```

## 🎨 Implementação Frontend

### **1. Estrutura de Páginas**
```
saas-juridico-frontend/src/app/company/processes/
├── page.tsx                    # Lista de processos (já existe)
├── [id]/
│   ├── page.tsx               # Página de detalhes do processo
│   ├── timeline/
│   │   └── page.tsx           # Timeline detalhada
│   ├── documents/
│   │   └── page.tsx           # Gestão de documentos
│   └── financial/
│       └── page.tsx           # Gestão financeira
```

### **2. Página Principal de Detalhes**
```typescript
// src/app/company/processes/[id]/page.tsx
export default function ProcessDetailPage({ params }: { params: { id: string } }) {
  const { process, loading } = useProcess(params.id);
  
  return (
    <div className="container mx-auto p-6">
      {/* Header com informações básicas */}
      <ProcessHeader process={process} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Timeline principal */}
        <div className="lg:col-span-2">
          <ProcessTimeline processId={params.id} />
        </div>
        
        {/* Sidebar com informações resumidas */}
        <div className="space-y-6">
          <ProcessInfo process={process} />
          <ProcessDeadlines processId={params.id} />
          <ProcessDocuments processId={params.id} />
          <ProcessFinancial processId={params.id} />
        </div>
      </div>
    </div>
  );
}
```

### **3. Componente ProcessHeader**
```typescript
// Componente para header do processo
function ProcessHeader({ process }: { process: Process }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{process.subject}</h1>
          <div className="flex items-center gap-4 mt-2 text-gray-600">
            <span>CNJ: {process.cnj_number || 'N/A'}</span>
            <span>Tribunal: {process.court || 'N/A'}</span>
            <span>Status: {process.status}</span>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline">Editar</Button>
          <Button>Novo Andamento</Button>
        </div>
      </div>
    </div>
  );
}
```

### **4. Componente ProcessTimeline**
```typescript
// Componente para timeline de andamentos
function ProcessTimeline({ processId }: { processId: string }) {
  const { timeline, loading, addEntry } = useProcessTimeline(processId);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Timeline de Andamentos</h2>
        <Button onClick={() => setShowAddEntry(true)}>
          Adicionar Andamento
        </Button>
      </div>
      
      <div className="space-y-4">
        {timeline.map((entry) => (
          <TimelineEntry key={entry.id} entry={entry} />
        ))}
      </div>
      
      {/* Modal para adicionar andamento */}
      <AddTimelineEntryModal 
        isOpen={showAddEntry}
        onClose={() => setShowAddEntry(false)}
        onSubmit={addEntry}
      />
    </div>
  );
}
```

### **5. Componente TimelineEntry**
```typescript
// Componente para cada entrada da timeline
function TimelineEntry({ entry }: { entry: TimelineEntry }) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'sentença': return <Gavel className="w-5 h-5" />;
      case 'audiência': return <Calendar className="w-5 h-5" />;
      case 'petição': return <FileText className="w-5 h-5" />;
      default: return <Circle className="w-5 h-5" />;
    }
  };
  
  const getColor = (type: string) => {
    switch (type) {
      case 'sentença': return 'text-green-600 bg-green-100';
      case 'audiência': return 'text-blue-600 bg-blue-100';
      case 'petição': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };
  
  return (
    <div className="flex gap-4">
      <div className={`p-2 rounded-full ${getColor(entry.type)}`}>
        {getIcon(entry.type)}
      </div>
      
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{entry.type}</h3>
          <span className="text-sm text-gray-500">
            {formatDate(entry.date)}
          </span>
        </div>
        
        <p className="text-gray-700 mt-1">{entry.description}</p>
        
        {entry.court_decision && (
          <div className="mt-2 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">{entry.court_decision}</p>
          </div>
        )}
        
        {entry.documents && entry.documents.length > 0 && (
          <div className="mt-2 flex gap-2">
            {entry.documents.map((doc) => (
              <Badge key={doc.id} variant="outline">
                {doc.name}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### **6. Componente ProcessDeadlines**
```typescript
// Componente para prazos críticos
function ProcessDeadlines({ processId }: { processId: string }) {
  const { deadlines, loading, addDeadline, completeDeadline } = useProcessDeadlines(processId);
  
  const criticalDeadlines = deadlines.filter(d => d.is_critical);
  const regularDeadlines = deadlines.filter(d => !d.is_critical);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Prazos</h3>
        <Button size="sm" onClick={() => setShowAddDeadline(true)}>
          Adicionar
        </Button>
      </div>
      
      {/* Prazos críticos */}
      {criticalDeadlines.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-red-600 mb-2">Críticos</h4>
          <div className="space-y-2">
            {criticalDeadlines.map((deadline) => (
              <DeadlineItem 
                key={deadline.id} 
                deadline={deadline}
                onComplete={completeDeadline}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Prazos regulares */}
      {regularDeadlines.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">Regulares</h4>
          <div className="space-y-2">
            {regularDeadlines.map((deadline) => (
              <DeadlineItem 
                key={deadline.id} 
                deadline={deadline}
                onComplete={completeDeadline}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### **7. Componente ProcessDocuments**
```typescript
// Componente para documentos
function ProcessDocuments({ processId }: { processId: string }) {
  const { documents, loading, uploadDocument } = useProcessDocuments(processId);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Documentos</h3>
        <Button size="sm" onClick={() => setShowUpload(true)}>
          Upload
        </Button>
      </div>
      
      <div className="space-y-2">
        {documents.map((doc) => (
          <DocumentItem key={doc.id} document={doc} />
        ))}
      </div>
      
      {/* Modal para upload */}
      <UploadDocumentModal 
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        onSubmit={uploadDocument}
      />
    </div>
  );
}
```

### **8. Componente ProcessFinancial**
```typescript
// Componente para informações financeiras
function ProcessFinancial({ processId }: { processId: string }) {
  const { financial, loading, addRecord } = useProcessFinancial(processId);
  
  const totalHonorarios = financial
    .filter(f => f.type === 'honorários')
    .reduce((sum, f) => sum + f.amount, 0);
    
  const totalCustas = financial
    .filter(f => f.type === 'custas')
    .reduce((sum, f) => sum + f.amount, 0);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Financeiro</h3>
        <Button size="sm" onClick={() => setShowAddRecord(true)}>
          Adicionar
        </Button>
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between">
          <span>Honorários:</span>
          <span className="font-semibold">
            {formatCurrency(totalHonorarios)}
          </span>
        </div>
        
        <div className="flex justify-between">
          <span>Custas:</span>
          <span className="font-semibold">
            {formatCurrency(totalCustas)}
          </span>
        </div>
        
        <hr />
        
        <div className="flex justify-between text-lg font-bold">
          <span>Total:</span>
          <span>{formatCurrency(totalHonorarios + totalCustas)}</span>
        </div>
      </div>
      
      {/* Lista de registros */}
      <div className="mt-4 space-y-2">
        {financial.map((record) => (
          <FinancialRecordItem key={record.id} record={record} />
        ))}
      </div>
    </div>
  );
}
```

## 🔧 Hooks Customizados

### **1. useProcessTimeline**
```typescript
// Hook para gerenciar timeline
export function useProcessTimeline(processId: string) {
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState(false);
  
  const fetchTimeline = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/company/processes/${processId}/timeline`);
      const data = await response.json();
      setTimeline(data);
    } catch (error) {
      console.error('Erro ao carregar timeline:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const addEntry = async (entryData: TimelineEntryCreate) => {
    try {
      const response = await fetch(`/api/v1/company/processes/${processId}/timeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entryData),
      });
      
      if (response.ok) {
        await fetchTimeline();
      }
    } catch (error) {
      console.error('Erro ao adicionar andamento:', error);
    }
  };
  
  useEffect(() => {
    fetchTimeline();
  }, [processId]);
  
  return { timeline, loading, addEntry, fetchTimeline };
}
```

### **2. useProcessDeadlines**
```typescript
// Hook para gerenciar prazos
export function useProcessDeadlines(processId: string) {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(false);
  
  const fetchDeadlines = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/company/processes/${processId}/deadlines`);
      const data = await response.json();
      setDeadlines(data);
    } catch (error) {
      console.error('Erro ao carregar prazos:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const addDeadline = async (deadlineData: DeadlineCreate) => {
    try {
      const response = await fetch(`/api/v1/company/processes/${processId}/deadlines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deadlineData),
      });
      
      if (response.ok) {
        await fetchDeadlines();
      }
    } catch (error) {
      console.error('Erro ao adicionar prazo:', error);
    }
  };
  
  const completeDeadline = async (deadlineId: string) => {
    try {
      const response = await fetch(
        `/api/v1/company/processes/${processId}/deadlines/${deadlineId}/complete`,
        { method: 'PUT' }
      );
      
      if (response.ok) {
        await fetchDeadlines();
      }
    } catch (error) {
      console.error('Erro ao completar prazo:', error);
    }
  };
  
  useEffect(() => {
    fetchDeadlines();
  }, [processId]);
  
  return { deadlines, loading, addDeadline, completeDeadline };
}
```

## 📱 Responsividade e UX

### **1. Layout Responsivo**
- **Desktop**: 3 colunas (timeline + sidebar)
- **Tablet**: 2 colunas (timeline + sidebar empilhada)
- **Mobile**: 1 coluna (timeline + sidebar empilhada)

### **2. Estados de Loading**
- Skeleton loaders para cada seção
- Loading spinners para ações
- Estados de erro com retry

### **3. Notificações**
- Toast notifications para ações
- Alertas para prazos críticos
- Confirmações para ações importantes

## 🚀 Próximos Passos

### **Fase 1 - Backend (1-2 dias)**
1. Implementar endpoints de timeline
2. Implementar endpoints de prazos
3. Implementar endpoints de documentos
4. Implementar endpoints financeiros
5. Criar schemas e validações

### **Fase 2 - Frontend (2-3 dias)**
1. Criar estrutura de páginas
2. Implementar componentes principais
3. Implementar hooks customizados
4. Implementar modais e formulários

### **Fase 3 - Integração (1 dia)**
1. Testar integração completa
2. Ajustar responsividade
3. Implementar notificações
4. Documentar funcionalidades

### **Fase 4 - Melhorias (1-2 dias)**
1. Implementar filtros avançados
2. Adicionar exportação de dados
3. Implementar busca em timeline
4. Adicionar atalhos de teclado

## 📊 Benefícios Esperados

### **1. Produtividade**
- Visualização rápida do status do processo
- Acesso fácil a documentos e prazos
- Ações rápidas sem navegação

### **2. Organização**
- Timeline visual clara
- Prazos destacados e organizados
- Documentos categorizados

### **3. Colaboração**
- Compartilhamento de informações
- Histórico completo de ações
- Notificações automáticas

**🎯 Resultado Final: Tela completa de acompanhamento de processos com todas as funcionalidades solicitadas!**
