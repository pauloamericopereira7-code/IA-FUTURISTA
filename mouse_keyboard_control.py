# -*- coding: utf-8 -*-
"""Client for the authenticated Windows desktop companion."""

from __future__ import annotations

import os
from pathlib import Path

import requests

HOST_URL = os.environ.get("IRIS_HOST_URL", "http://host.docker.internal:8743").rstrip("/")
TOKEN_FILE = Path(os.environ.get("IRIS_HOST_TOKEN_FILE", "/run/iris-host/token"))


def _host_action(action: str, params: dict) -> dict:
    try:
        token = TOKEN_FILE.read_text(encoding="ascii").strip()
        if not token:
            return {"status": "error", "message": "Token da ponte do PC vazio."}
        response = requests.post(
            f"{HOST_URL}/api/action",
            json={"action": action, "params": params},
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        data = response.json()
        if not response.ok:
            return {"status": "error", "message": data.get("message", "Ponte do PC recusou a ação.")}
        return data
    except FileNotFoundError:
        return {"status": "error", "message": "Ponte do PC não iniciada. Abra o atalho da Íris."}
    except (OSError, requests.RequestException, ValueError) as exc:
        return {"status": "error", "message": f"Ponte do PC indisponível: {exc}"}


def host_companion_available() -> bool:
    try:
        token = TOKEN_FILE.read_text(encoding="ascii").strip()
        response = requests.get(
            f"{HOST_URL}/health",
            headers={"Authorization": f"Bearer {token}"},
            timeout=1.5,
        )
        return response.ok
    except (OSError, requests.RequestException):
        return False


def move_mouse(x: int, y: int) -> dict:
    return _host_action("move_mouse", {"x": x, "y": y})


def click_mouse(button: str = "left", clicks: int = 1) -> dict:
    return _host_action("click", {"button": button, "clicks": clicks})


def type_text(text: str, interval: float = 0.02) -> dict:
    return _host_action("type", {"text": text, "interval": interval})


def press_key(key: str) -> dict:
    return _host_action("press_key", {"key": key})


def hotkey(keys: list[str]) -> dict:
    return _host_action("hotkey", {"keys": keys})


def open_url(url: str) -> dict:
    return _host_action("open_url", {"url": url})


def get_mouse_position() -> dict:
    return _host_action("get_position", {})


def screenshot_save(path: str = "") -> dict:
    return _host_action("screenshot", {})


def execute_mouse_keyboard_action(action: str, params: dict) -> dict:
    handlers = {
        "move_mouse": lambda: move_mouse(params.get("x", -1), params.get("y", -1)),
        "click": lambda: click_mouse(params.get("button", "left"), params.get("clicks", 1)),
        "type": lambda: type_text(params.get("text", ""), params.get("interval", 0.02)),
        "press_key": lambda: press_key(params.get("key", "enter")),
        "hotkey": lambda: hotkey(params.get("keys", [])),
        "open_url": lambda: open_url(params.get("url", "")),
        "get_position": get_mouse_position,
        "screenshot": screenshot_save,
    }
    handler = handlers.get(action)
    if not handler:
        return {"status": "error", "message": f"Ação desconhecida: {action}"}
    return handler()