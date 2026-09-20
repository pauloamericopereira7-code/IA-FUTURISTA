# IA Futurista — Sistema de Automações e Cache Inteligente

## ✨ Novas Funcionalidades

### 1. **Cache Inteligente com Scraping Web**
Sistema que armazena conhecimento com versionamento e TTL:

- **Almacenamento em SQLite** com índices otimizados
- **Web scraping responsável** com rate limiting
- **Versionamento** de conhecimento
- **Hits tracking** para análise de uso
- **TTL configurável** por entrada

```python
from knowledge_cache import cache

# Scrape uma URL e cache por 24h
result = cache.scrape_safely("https://example.com", selector="body")

# Buscar no cache
cached = cache.get("web:hash")

# Adicionar conhecimento estruturado
cache.add_knowledge(
    topic="Python async",
    content="Async permite...",
    sources=["docs.python.org"]
)

# Buscar conhecimento
results = cache.search_knowledge("async python")

# Estatísticas
stats = cache.get_stats()
```

### 2. **Fila de Automações com Aprovação**
Todas as tarefas automatizadas requerem aprovação do usuário (configurável):

- **Filas persistentes** em SQLite
- **Estados completos**: pending → approved → running → completed/failed
- **Auditoria completa** de todas as ações
- **Logs integrados** por tarefa

```python
from automation_queue import queue, AutomationTask, TaskStatus

# Criar tarefa
task = AutomationTask(
    name="Backup diário",
    description="Fazer backup dos projetos",
    action="run_command",
    params={"command": "tar -czf backup.tar.gz ./projetos"},
    requires_approval=True
)

# Enfileirar
task_id = queue.enqueue(task)

# Aprovar e executar
queue.approve(task_id)
result = queue.execute(task_id)

# Ver histórico
history = queue.get_history(limit=50)
```

### 3. **Interface de Controle em Streamlit**

Painel **⚙️ Automações** com 4 abas:

#### **📋 Fila**
- Visualizar todas as tarefas aguardando aprovação
- Botões para aprovar/rejeitar
- Detalhes técnicos expansíveis

#### **🚀 Executar**
- Criar novas automações via formulário
- Tipos de ação: run_command, run_script, write_file, scrape_web
- Toggle para ativar/desativar aprovação

#### **📊 Histórico**
- Ver todas as execuções passadas
- Filtrar por status
- Resultados e erros visíveis

#### **💾 Cache**
- Estatísticas do cache (entries, hits, tamanho)
- Adicionar conhecimento manualmente
- Fazer scrape de URLs
- Limpar cache quando necessário

### 4. **APIs RESTful para Integração**

```bash
# Criar tarefa
POST /api/automation/task/create
{
  "name": "Atualizar documentação",
  "description": "Faz deploy da doc",
  "action": "run_command",
  "params": {"command": "make docs"},
  "requires_approval": true
}

# Listar pendentes
GET /api/automation/tasks/pending

# Aprovar/rejeitar
POST /api/automation/task/approve
{
  "task_id": "abc123",
  "approved": true,
  "reason": ""
}

# Histórico
GET /api/automation/tasks/history?limit=50

# Cache stats
GET /api/cache/stats

# Limpar cache
POST /api/cache/clear
```

## 🔒 Segurança & Confiabilidade

✅ **Aprovação obrigatória** de tarefas por padrão  
✅ **Auditoria completa** de todos os eventos  
✅ **Logs persistentes** em banco de dados  
✅ **Sandbox de execução** (limites de timeout)  
✅ **Validação de parâmetros** antes de rodar  
✅ **Rollback automático** em caso de erro  
✅ **Histórico completo** de todas as ações  

## 📊 Exemplos de Uso

### Automação de Backup
```python
task = AutomationTask(
    name="Backup semanal",
    description="Backup de todos os projetos",
    action="run_command",
    params={
        "command": "zip -r backup_$(date +%Y%m%d).zip ./projetos"
    }
)
queue.enqueue(task)
```

### Scrape e Cache de Documentação
```python
# Scrape automaticamente
result = cache.scrape_safely(
    "https://docs.python.org/3/library/asyncio.html",
    selector=".section",
    cache_ttl=168  # 1 week
)

# Adicionar ao conhecimento
cache.add_knowledge(
    topic="Python asyncio",
    content=result["content"],
    sources=["https://docs.python.org"]
)
```

### Geração Automática de Relatórios
```python
task = AutomationTask(
    name="Gerar relatório",
    description="Cria relatório de performance",
    action="run_script",
    params={
        "script": """
import json
from datetime import datetime

report = {
    'data': datetime.now().isoformat(),
    'status': 'ok'
}
print(json.dumps(report))
"""
    }
)
queue.enqueue(task)
```

## 🚀 Como Usar

1. **Abra a UI** em http://127.0.0.1:8742
2. **Clique em "⚙️ Automações"** no final da página
3. **Navegue pelas abas**:
   - 📋 **Fila**: ver tarefas pendentes
   - 🚀 **Executar**: criar nova tarefa
   - 📊 **Histórico**: ver o que rodou
   - 💾 **Cache**: gerenciar conhecimento

4. **Crie uma tarefa** → Clique em Executar → Aprove quando aparecer na fila

## 🔧 Configuração

### Variáveis de ambiente
```bash
# Configurar diretório de cache
export FUTURISTA_CACHE_DIR="/caminho/customizado"

# Timeout de execução
export AUTOMATION_TIMEOUT=120
```

### Via Docker Compose
```yaml
environment:
  - OLLAMA_URL=http://host.docker.internal:11434
  - OLLAMA_MODEL=qwen2.5-coder:7b
  - AUTOMATION_TIMEOUT=120
```

## 📈 Monitoramento

Via `/api/cache/stats`:
```json
{
  "cache_entries": 142,
  "total_hits": 5203,
  "knowledge_base_entries": 28,
  "cache_size_mb": 4.2
}
```

## ⚠️ Limitações Atuais

- Timeout de execução: **60 segundos** (configurável)
- Cache máximo: **5000 caracteres por scrape**
- Histórico: últimas **100 tarefas** na memória
- Banda: respeita rate limiting de DuckDuckGo/Google

---

**Tudo auditado, rastreado e seguro. Você está no controle.** 🎯
