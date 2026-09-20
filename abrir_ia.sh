#!/bin/bash
cd "$(dirname "$0")"
# Sobe servidor se offline
if ! curl -sf http://127.0.0.1:8742/api/status >/dev/null 2>&1; then
  SESSION="futurista-app"
  tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION" 2>/dev/null || \
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION" -c "$(pwd)" -- \
    python3 -m uvicorn server:app --host 0.0.0.0 --port 8742
  sleep 2
fi
# Garante Ollama
if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  tmux -f /exec-daemon/tmux.portal.conf has-session -t "=ollama-serve" 2>/dev/null || \
  tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "ollama-serve" -- ollama serve
  sleep 2
fi
xdg-open "http://127.0.0.1:8742" 2>/dev/null || sensible-browser "http://127.0.0.1:8742" 2>/dev/null
