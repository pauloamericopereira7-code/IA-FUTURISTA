let sessaoId = null;
let enviando = false;
let imagemSelecionada = null;

const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatHistory = document.getElementById("chat-history");
const chatTitle = document.getElementById("chat-title");
const chatScroll = document.getElementById("chat-scroll");
const imageInput = document.getElementById("image-input");
const attachmentPreview = document.getElementById("attachment-preview");
const agentSelect = document.getElementById("agent-select");
const pcAccessToggle = document.getElementById("pc-access-toggle");
const pcAccessStatus = document.getElementById("pc-access-status");
const agentNames = {
  geral: "Geral",
  programacao: "Programação",
  pesquisa: "Pesquisa",
  visao: "Visão",
  automacao: "Automação",
  design: "Design",
  dados: "Dados",
  escrita: "Escrita",
  suporte_windows: "Suporte Windows",
};

async function api(path, opts = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 300000);
  try {
    const res = await fetch(path, { ...opts, signal: ctrl.signal, headers: { "Content-Type": "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } finally {
    clearTimeout(timer);
  }
}

function escapeHtml(t) {
  return (t || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
    `<pre><code>${code.trim()}</code></pre>`
  );
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\n/g, "<br>");
  return html;
}

function renderMessages(msgs) {
  chatMessages.innerHTML = "";
  (msgs || []).forEach((m) => {
    if (m.role === "user") {
      const div = document.createElement("div");
      div.className = "msg-user";
      div.textContent = m.content;
      if (m.imagem) {
        const image = document.createElement("img");
        image.className = "message-image";
        image.src = m.imagem;
        image.alt = "Imagem enviada";
        div.appendChild(image);
      }
      chatMessages.appendChild(div);
    } else {
      if (m.worked) {
        const w = document.createElement("div");
        w.className = "worked";
        w.textContent = `✓ Concluído em ${m.worked}s`;
        chatMessages.appendChild(w);
      }
      if (m.agente) {
        const agentLabel = document.createElement("div");
        agentLabel.className = "agent-label";
        agentLabel.textContent = `Íris · ${agentNames[m.agente] || agentNames.geral}`;
        chatMessages.appendChild(agentLabel);
      }
      const div = document.createElement("div");
      div.className = "msg-ai";
      div.innerHTML = renderMarkdown(m.content);
      chatMessages.appendChild(div);
      if (m.preview) {
        const card = document.createElement("div");
        card.className = "preview-card";
        card.innerHTML = `
          <div class="left">
            <div class="thumb"></div>
            <div class="info">
              <h3>${escapeHtml(m.preview.title)}</h3>
              <p>${escapeHtml(m.preview.desc)}</p>
            </div>
          </div>
          <button class="preview-btn" onclick="window.open('${m.preview.url}','_blank')">Preview</button>`;
        chatMessages.appendChild(card);
      }
    }
  });
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

function renderHistory(sessoes) {
  chatHistory.innerHTML = "";
  sessoes.slice().reverse().forEach((s) => {
    const el = document.createElement("div");
    el.className = "history-item" + (s.id === sessaoId ? " active" : "");
    const mins = s.msgs?.length ? "1m" : "agora";
    el.innerHTML = `<span>${s.id === sessaoId ? '<span class="dot"></span>' : ""}${escapeHtml(s.titulo)}</span><span class="time">${mins}</span>`;
    el.onclick = () => loadSessao(s);
    chatHistory.appendChild(el);
  });
}

async function loadSessao(s) {
  sessaoId = s.id;
  chatTitle.textContent = s.titulo;
  renderMessages(s.msgs || []);
  const sessoes = await api("/api/sessoes");
  renderHistory(sessoes);
}

async function init() {
  const status = await api("/api/status");
  const visionActive = Boolean(status.capacidades?.visao);
  document.getElementById("cloud-status").textContent = status.ollama ? "Ollama local conectado" : "Ollama desconectado";
  document.getElementById("capability-status").textContent = status.ollama
    ? (visionActive ? "Texto e visão ativos" : "Chat ativo · modelo visual ausente")
    : "Modelo local desconectado";
  document.getElementById("status-indicator").classList.toggle("online", Boolean(status.ollama));
  document.getElementById("model-label").textContent = status.modelo_padrao || "Ollama";
  const pcAccess = status.acesso_pc || {};
  pcAccessToggle.checked = Boolean(pcAccess.ativo);
  pcAccessToggle.disabled = !pcAccess.conectado && !pcAccess.ativo;
  pcAccessStatus.textContent = !pcAccess.conectado
    ? "Ponte Windows desconectada"
    : (pcAccess.ativo ? "Mouse e teclado autorizados" : "Acesso revogado");
  if (!status.ollama) {
    const aviso = document.createElement("div");
    aviso.className = "msg-ai";
    aviso.innerHTML = "<strong>Ollama desconectado</strong><br>Inicie o Ollama para conversar com Íris.";
    chatMessages.appendChild(aviso);
  }

  const sessoes = await api("/api/sessoes");
  renderHistory(sessoes);
  if (sessoes.length) await loadSessao(sessoes[0]);
}

async function enviar() {
  const texto = chatInput.value.trim();
  const anexo = imagemSelecionada;
  if ((!texto && !anexo) || enviando) return;
  const mensagem = texto || "Analise a imagem anexada.";
  enviando = true;
  chatInput.value = "";
  chatInput.style.height = "auto";

  const userDiv = document.createElement("div");
  userDiv.className = "msg-user";
  userDiv.textContent = mensagem;
  if (anexo) {
    const image = document.createElement("img");
    image.className = "message-image";
    image.src = anexo.dataUrl;
    image.alt = "Imagem enviada";
    userDiv.appendChild(image);
  }
  chatMessages.appendChild(userDiv);

  const thinking = document.createElement("div");
  thinking.className = "thinking";
  thinking.textContent = "Íris está pensando...";
  chatMessages.appendChild(thinking);
  chatScroll.scrollTop = chatScroll.scrollHeight;

  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        mensagem,
        sessao_id: sessaoId,
        imagem_b64: anexo?.base64 || null,
        agente: agentSelect.value,
      }),
    });
    sessaoId = data.sessao_id;
    thinking.remove();
    renderMessages(data.sessao.msgs);
    if (imagemSelecionada === anexo && anexo) {
      imagemSelecionada = null;
      attachmentPreview.hidden = true;
      imageInput.value = "";
    }
    chatTitle.textContent = data.sessao.titulo;
    const sessoes = await api("/api/sessoes");
    renderHistory(sessoes);
  } catch (e) {
    thinking.remove();
    const errDiv = document.createElement("div");
    errDiv.className = "msg-ai";
    errDiv.innerHTML = `<strong>Erro</strong><br>${escapeHtml(e.message || "Falha na conexão")}`;
    chatMessages.appendChild(errDiv);
  }
  enviando = false;
}

document.getElementById("btn-send").onclick = enviar;
pcAccessToggle.addEventListener("change", async () => {
  const enabled = pcAccessToggle.checked;
  pcAccessToggle.disabled = true;
  try {
    const access = await api("/api/acesso-pc", {
      method: "POST",
      body: JSON.stringify({ enabled }),
    });
    pcAccessToggle.checked = Boolean(access.ativo);
    pcAccessStatus.textContent = access.conectado
      ? (access.ativo ? "Mouse e teclado autorizados" : "Acesso revogado")
      : "Ponte Windows desconectada";
  } catch (e) {
    pcAccessToggle.checked = !enabled;
    pcAccessStatus.textContent = "Não foi possível alterar o acesso";
  } finally {
    pcAccessToggle.disabled = false;
  }
});
document.getElementById("btn-image").onclick = () => imageInput.click();
document.getElementById("remove-attachment").onclick = () => {
  imagemSelecionada = null;
  imageInput.value = "";
  attachmentPreview.hidden = true;
};
imageInput.addEventListener("change", () => {
  const arquivo = imageInput.files?.[0];
  if (!arquivo) return;
  if (!/^image\/(png|jpeg|webp)$/.test(arquivo.type)) {
    alert("Escolha uma imagem PNG, JPEG ou WebP.");
    imageInput.value = "";
    return;
  }
  if (arquivo.size > 8 * 1024 * 1024) {
    alert("A imagem deve ter até 8 MB.");
    imageInput.value = "";
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    const dataUrl = String(reader.result || "");
    imagemSelecionada = { dataUrl, base64: dataUrl.split(",")[1], nome: arquivo.name };
    document.getElementById("attachment-image").src = dataUrl;
    document.getElementById("attachment-name").textContent = arquivo.name;
    attachmentPreview.hidden = false;
  };
  reader.readAsDataURL(arquivo);
});
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    enviar();
  }
});
chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = chatInput.scrollHeight + "px";
});

document.getElementById("btn-new-chat").onclick = async () => {
  const s = await api("/api/sessoes", { method: "POST", body: JSON.stringify({ titulo: "Nova conversa" }) });
  sessaoId = s.id;
  chatTitle.textContent = s.titulo;
  renderMessages([]);
  const sessoes = await api("/api/sessoes");
  renderHistory(sessoes);
};

init();
