let sessaoId = null;
let enviando = false;

const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatHistory = document.getElementById("chat-history");
const chatTitle = document.getElementById("chat-title");
const chatScroll = document.getElementById("chat-scroll");

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
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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
  msgs.forEach((m) => {
    if (m.role === "user") {
      const div = document.createElement("div");
      div.className = "msg-user";
      div.textContent = m.content;
      chatMessages.appendChild(div);
    } else {
      if (m.worked) {
        const w = document.createElement("div");
        w.className = "worked";
        w.innerHTML = `✓ Worked for ${m.worked}s <span style="opacity:.6">▾</span>`;
        chatMessages.appendChild(w);
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
  document.getElementById("cloud-status").textContent = status.ollama ? "☁ Cloud" : "⚠ Offline — rode: ollama serve";
  document.getElementById("model-label").textContent = status.identidade?.nome || "Auto";
  if (!status.ollama) {
    const aviso = document.createElement("div");
    aviso.className = "msg-ai";
    aviso.innerHTML = "<strong>⚠ Ollama offline</strong><br>Execute no terminal: <code>ollama serve</code> e recarregue a página.";
    chatMessages.appendChild(aviso);
  }

  const sessoes = await api("/api/sessoes");
  renderHistory(sessoes);
  if (sessoes.length) await loadSessao(sessoes[0]);
}

async function enviar() {
  const texto = chatInput.value.trim();
  if (!texto || enviando) return;
  enviando = true;
  chatInput.value = "";
  chatInput.style.height = "auto";

  const userDiv = document.createElement("div");
  userDiv.className = "msg-user";
  userDiv.textContent = texto;
  chatMessages.appendChild(userDiv);

  const thinking = document.createElement("div");
  thinking.className = "thinking";
  thinking.textContent = "Agente Auto trabalhando...";
  chatMessages.appendChild(thinking);
  chatScroll.scrollTop = chatScroll.scrollHeight;

  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ mensagem: texto, sessao_id: sessaoId }),
    });
    sessaoId = data.sessao_id;
    thinking.remove();
    renderMessages(data.sessao.msgs);
    chatTitle.textContent = data.sessao.titulo;
    const sessoes = await api("/api/sessoes");
    renderHistory(sessoes);
    document.getElementById("progress-text").textContent = "3/3";
    document.getElementById("progress-fill").style.width = "100%";
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
  const s = await api("/api/sessoes", { method: "POST", body: JSON.stringify({ titulo: "Novo chat" }) });
  sessaoId = s.id;
  chatTitle.textContent = s.titulo;
  renderMessages([]);
  const sessoes = await api("/api/sessoes");
  renderHistory(sessoes);
};

init();
