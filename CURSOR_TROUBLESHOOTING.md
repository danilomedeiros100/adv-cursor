# 🔧 Cursor Desktop - Guia de Solução de Problemas

## ❌ Problemas Comuns e Soluções

### **1. Chat Para de Responder**

#### **Causas:**
- Limite de contexto atingido
- Conexão de internet instável
- Cache corrompido
- Memory leak do Cursor

#### **Soluções:**
```bash
# 1. Reiniciar Cursor completamente
Ctrl+Shift+P → "Developer: Reload Window"

# 2. Limpar cache (feche o Cursor primeiro)
# Windows:
del /s /q "%APPDATA%\Cursor\User\workspaceStorage\*"
del /s /q "%APPDATA%\Cursor\logs\*"

# Mac:
rm -rf ~/Library/Application\ Support/Cursor/User/workspaceStorage/*
rm -rf ~/Library/Application\ Support/Cursor/logs/*

# Linux:
rm -rf ~/.config/Cursor/User/workspaceStorage/*
rm -rf ~/.config/Cursor/logs/*

# 3. Verificar conexão
ping github.com
```

### **2. Perda de Contexto**

#### **Soluções:**
- Use **@** para referenciar arquivos específicos
- Mantenha um arquivo de contexto (como este)
- Salve conversas importantes
- Use comandos específicos por módulo

#### **Exemplo de Uso com Contexto:**
```
@README.md @backend/main.py 
Preciso implementar uma nova funcionalidade no módulo de processos
```

### **3. Performance Lenta**

#### **Otimizações:**
```json
// settings.json
{
  "cursor.chat.maxTokens": 4000,
  "cursor.workspace.indexing": false,
  "cursor.chat.enableCodeContext": false
}
```

### **4. Erros de Sincronização**

#### **Comandos de Diagnóstico:**
```bash
# Verificar status do Git
git status
git log --oneline -5

# Verificar integridade do workspace
cursor --version
cursor --list-extensions
```

## 🚀 Configurações Recomendadas

### **Configurações Otimizadas (.cursor/cursor-settings.json):**
```json
{
  "cursor.chat.maxTokens": 8000,
  "cursor.chat.temperature": 0.7,
  "cursor.chat.clearContextOnRestart": false,
  "cursor.chat.persistHistory": true,
  "cursor.chat.saveConversations": true,
  "cursor.general.enableLogging": true,
  "cursor.chat.contextWindow": "large",
  "cursor.chat.model": "claude-3.5-sonnet",
  "cursor.chat.enableCodeContext": true,
  "cursor.chat.maxHistoryLength": 50,
  "cursor.workspace.indexing": true,
  "cursor.workspace.enableSymbolSearch": true,
  "cursor.workspace.enableSemanticSearch": true
}
```

## 💡 Dicas para Manter Contexto

### **1. Estruture Conversas por Tópico**
- Uma conversa para cada módulo/funcionalidade
- Use títulos descritivos nas conversas
- Salve conversas importantes

### **2. Use Referências Específicas**
```
# Bom ✅
@backend/apps/processes/router.py 
Implementar validação no endpoint de criação

# Ruim ❌
Implementar validação nos processos
```

### **3. Mantenha Arquivos de Contexto**
- `context-manager.md` - Estado atual do projeto
- `TROUBLESHOOTING.md` - Este arquivo
- `TODO.md` - Lista de tarefas pendentes

### **4. Comandos Úteis para Contexto**
```bash
# Ver estrutura do projeto
tree -I 'node_modules|__pycache__|.git' -L 3

# Status dos serviços
docker-compose ps

# Logs recentes
docker-compose logs --tail=20 backend
```

## 🔄 Rotina de Manutenção

### **Diária:**
- Reiniciar Cursor a cada 3-4 horas de uso
- Limpar logs antigos
- Verificar status dos containers

### **Semanal:**
- Limpar cache completo
- Atualizar Cursor para última versão
- Backup das conversas importantes

### **Comandos de Manutenção:**
```bash
# Limpeza rápida
docker system prune -f
git gc --aggressive

# Verificação de saúde
docker-compose exec backend python -c "print('Backend OK')"
curl http://localhost:8000/health
```

## 📞 Quando Buscar Ajuda

### **Sintomas de Problemas Graves:**
- Cursor não inicia
- Erro de corrupção de dados
- Performance extremamente lenta
- Perda constante de contexto

### **Logs para Análise:**
- Windows: `%APPDATA%\Cursor\logs\`
- Mac: `~/Library/Application Support/Cursor/logs/`
- Linux: `~/.config/Cursor/logs/`

---

**Mantenha este arquivo sempre atualizado com novos problemas e soluções encontrados!**