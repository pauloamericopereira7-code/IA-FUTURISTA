# 🚀 COMO USAR O ATALHO DE INICIALIZAÇÃO

## ✅ Atalho Criado na Area de Trabalho

Seu atalho **"IA Futurista"** foi criado em:
```
C:\Users\Administrador\OneDrive\Desktop\IA Futurista.lnk
```

---

## 📋 Pré-requisitos (execute UMA VEZ antes de usar)

### 1. Docker Desktop
- Baixe: https://www.docker.com/products/docker-desktop
- Instale e abra
- Deixe rodando em background

### 2. Ollama
- Baixe: https://ollama.ai
- Instale
- Execute no terminal: `ollama serve`
- Deixe rodando em background

### 3. Modelo Ollama
Abra PowerShell e execute:
```powershell
ollama pull qwen2.5-coder:7b
```

---

## 🎯 COMO INICIAR A IA FUTURISTA

### Opção 1: Atalho (MAIS FÁCIL)
1. **Vá à Area de Trabalho**
2. **Clique duplo** em **"IA Futurista"**
3. Espere carregar (2-3 minutos na primeira vez)
4. Navegador abre automaticamente em **http://127.0.0.1:8742**

### Opção 2: Manual (Linha de Comando)
```bash
cd C:\Users\Administrador\Downloads\IA_Futurista\futurista
docker compose up -d
start http://127.0.0.1:8742
```

---

## 🎮 O QUE FAZER QUANDO ABRIR

### 1. Chat Simples
```
Você: "Olá, tudo bem?"
IA: Responde em português, com contexto completo
```

### 2. Automações
```
Menu esquerdo → ⚙️ Automações
→ 🚀 Executar
→ Escolha a ação (comando, script, arquivo, etc.)
→ Clique "Criar Tarefa"
→ Aprove na fila
```

### 3. Controle de Mouse/Teclado
```
⚙️ Automações → Escolha a ação de mouse/teclado
Exemplos:
- Mover mouse para coordenada
- Digitar texto
- Clicar
- Pressionar teclas (Ctrl+C, Enter, etc.)
```

### 4. Cache de Conhecimento
```
⚙️ Automações → 💾 Cache
- Adicionar conhecimento
- Fazer scrape de URLs
- Ver estatísticas
```

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Erro: "Docker não encontrado"
```
Solução: Instale Docker Desktop
https://www.docker.com/products/docker-desktop
```

### Erro: "Ollama offline"
```
Solução: Abra terminal e execute:
ollama serve
```

### Porta 8742 já em uso
```
Solução 1: Feche outro programa usando porta 8742
Solução 2: Edite futurista/docker-compose.yml linha 6:
ports: ["8743:8742"]  # Mude 8742 para 8743
```

### Lentidão na primeira inicialização
```
Normal! Primeira vez:
- Baixa imagem Docker (~2GB)
- Inicia container
- Carrega Ollama
- Carrega modelo (500MB)

Próximas vezes: instantâneo (10 segundos)
```

---

## 🎨 PERSONALIZAR O ATALHO

### Mudar ícone
1. Clique direito em "IA Futurista.lnk"
2. Propriedades
3. Avançado
4. Mudar ícone (escolha um do System32\Shell32.dll)

### Iniciar minimizado
1. Clique direito em "IA Futurista.lnk"
2. Propriedades
3. Executar: Minimizado

### Iniciar como Administrador
1. Clique direito em "IA Futurista.lnk"
2. Propriedades → Avançado
3. Marque "Executar como administrador"

---

## 🔗 LINKS ÚTEIS

- **IA Futurista**: http://127.0.0.1:8742
- **GitHub**: https://github.com/pauloamericopereira7-code/IA-FUTURISTA
- **Docker Hub**: https://hub.docker.com
- **Ollama**: https://ollama.ai
- **Documentação**: futurista/AUTOMATION_GUIDE.md

---

## 📞 SUPORTE

Se tiver problema:
1. Veja logs: `docker logs ia-futurista`
2. Reinicie: `docker compose restart`
3. Recrie: `docker compose down && docker compose up -d`

---

## ✨ VOCÊ AGORA TEM:

✅ IA rodando localmente no seu PC
✅ Controle total de mouse/teclado
✅ Automações auditadas
✅ Cache inteligente
✅ 16 modelos LLM disponíveis
✅ Atalho fácil na area de trabalho

**Aproveite! 🚀**
