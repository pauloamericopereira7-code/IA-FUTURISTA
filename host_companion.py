# -*- coding: utf-8 -*-
"""Authenticated Windows desktop bridge for the Dockerized Iris app."""

from __future__ import annotations

import base64
import ctypes
import ctypes.wintypes
import ipaddress
import json
import os
import secrets
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / ".iris_host_token"
PORT = int(os.environ.get("IRIS_HOST_PORT", "8743"))
DOCKER_SUBNET = ipaddress.ip_network(os.environ.get("IRIS_DOCKER_SUBNET", "172.22.0.0/16"))

KEYS = {
    "enter": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "space": 0x20,
    "backspace": 0x08,
    "delete": 0x2E,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
    "ctrl": 0x11,
    "alt": 0x12,
    "shift": 0x10,
    "win": 0x5B,
}


def ensure_token() -> str:
    if not TOKEN_FILE.exists():
        TOKEN_FILE.write_text(secrets.token_urlsafe(48), encoding="ascii")
    return TOKEN_FILE.read_text(encoding="ascii").strip()


def key_code(key: str) -> int:
    normalized = key.lower()
    if normalized in KEYS:
        return KEYS[normalized]
    if len(normalized) == 1 and normalized.isascii() and normalized.isalnum():
        return ord(normalized.upper())
    if normalized.startswith("f") and normalized[1:].isdigit():
        number = int(normalized[1:])
        if 1 <= number <= 12:
            return 0x70 + number - 1
    raise ValueError("Tecla não permitida.")


def execute_action(action: str, params: dict) -> dict:
    if action == "open_url":
        url = str(params.get("url", "")).strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Informe uma URL http ou https válida, sem credenciais embutidas.")
        opened = webbrowser.open(url, new=2, autoraise=True)
        if not opened:
            raise OSError("O navegador padrão do Windows não conseguiu abrir a página.")
        return {"status": "ok", "url": url, "message": "Página aberta no navegador padrão do Windows."}

    user32 = ctypes.windll.user32

    if action == "get_position":
        point = ctypes.wintypes.POINT()
        if not user32.GetCursorPos(ctypes.byref(point)):
            raise OSError("Não foi possível obter a posição do cursor.")
        return {"status": "ok", "x": point.x, "y": point.y}

    if action == "move_mouse":
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        x, y = int(params.get("x", -1)), int(params.get("y", -1))
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError("As coordenadas estão fora da tela.")
        if not user32.SetCursorPos(x, y):
            raise OSError("Não foi possível mover o cursor.")
        return {"status": "ok", "x": x, "y": y}

    if action == "click":
        button = str(params.get("button", "left")).lower()
        clicks = int(params.get("clicks", 1))
        flags = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010), "middle": (0x0020, 0x0040)}
        if button not in flags or not 1 <= clicks <= 3:
            raise ValueError("Botão ou quantidade de cliques inválida.")
        down, up = flags[button]
        for index in range(clicks):
            user32.mouse_event(down, 0, 0, 0, 0)
            user32.mouse_event(up, 0, 0, 0, 0)
            if index + 1 < clicks:
                time.sleep(0.08)
        return {"status": "ok", "button": button, "clicks": clicks}

    if action == "type":
        text = str(params.get("text", ""))
        if len(text) > 1000:
            raise ValueError("O texto excede o limite de 1000 caracteres.")
        interval = max(0.0, min(float(params.get("interval", 0.02)), 0.05))
        for character in text:
            encoded = character.encode("utf-16-le")
            for offset in range(0, len(encoded), 2):
                code_unit = int.from_bytes(encoded[offset : offset + 2], "little")
                user32.keybd_event(0, code_unit, 0x0004, 0)
                user32.keybd_event(0, code_unit, 0x0004 | 0x0002, 0)
            if interval:
                time.sleep(interval)
        return {"status": "ok", "characters": len(text)}

    if action == "press_key":
        code = key_code(str(params.get("key", "enter")))
        user32.keybd_event(code, 0, 0, 0)
        user32.keybd_event(code, 0, 0x0002, 0)
        return {"status": "ok", "key": str(params.get("key", "enter"))}

    if action == "hotkey":
        keys = params.get("keys", [])
        if not isinstance(keys, list) or not 2 <= len(keys) <= 4:
            raise ValueError("O atalho deve conter de 2 a 4 teclas.")
        codes = [key_code(str(key)) for key in keys]
        for code in codes:
            user32.keybd_event(code, 0, 0, 0)
        for code in reversed(codes):
            user32.keybd_event(code, 0, 0x0002, 0)
        return {"status": "ok", "keys": keys}

    if action == "screenshot":
        from PIL import ImageGrab

        image = ImageGrab.grab().convert("RGB")
        image.thumbnail((1600, 1000))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=82, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return {"status": "ok", "image_b64": encoded}

    raise ValueError("Ação de desktop desconhecida.")


class Handler(BaseHTTPRequestHandler):
    server_version = "IrisDesktop/1.0"

    def _authorized(self) -> bool:
        try:
            remote = ipaddress.ip_address(self.client_address[0])
        except ValueError:
            return False
        if not (remote.is_loopback or remote in DOCKER_SUBNET):
            return False
        supplied = self.headers.get("Authorization", "")
        return secrets.compare_digest(supplied, f"Bearer {ensure_token()}")

    def _send_json(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(404, {"status": "error", "message": "Não encontrado."})
        elif not self._authorized():
            self._send_json(403, {"status": "error", "message": "Acesso negado."})
        else:
            self._send_json(200, {"status": "ok", "service": "iris-desktop"})

    def do_POST(self) -> None:
        if self.path != "/api/action":
            self._send_json(404, {"status": "error", "message": "Não encontrado."})
            return
        if not self._authorized():
            self._send_json(403, {"status": "error", "message": "Acesso negado."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("Tamanho da solicitação inválido.")
            request = json.loads(self.rfile.read(length))
            result = execute_action(request.get("action", ""), request.get("params", {}))
            self._send_json(200, result)
        except Exception as exc:
            self._send_json(400, {"status": "error", "message": str(exc)})

    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {self.client_address[0]} {format % args}")


def main() -> None:
    token = ensure_token()
    if "--init-token" in sys.argv:
        print("Chave local inicializada.")
        return
    try:
        server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048 or exc.errno == 98:
            print("Ponte de desktop Íris já está ativa.")
            return
        raise
    print(f"Ponte de desktop Íris ativa na porta {PORT}; rede permitida: {DOCKER_SUBNET}.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
