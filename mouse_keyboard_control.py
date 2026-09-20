# -*- coding: utf-8 -*-
"""Ferramentas de controle de mouse e teclado."""

import json
import logging
import subprocess
import sys
import time
from typing import Optional

logger = logging.getLogger("mouse_keyboard")
logger.setLevel(logging.DEBUG)


def move_mouse(x: int, y: int) -> dict:
    """Move o mouse para coordenadas (x, y)."""
    try:
        if sys.platform == "win32":
            # Windows: usar pyautogui via PowerShell
            script = f"""
import pyautogui
pyautogui.moveTo({x}, {y}, duration=0.5)
print('Mouse movido para ({x}, {y})')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {"status": "ok", "message": f"Mouse em ({x}, {y})", "output": result.stdout}
        else:
            return {"status": "error", "message": "Mouse control só suporta Windows por enquanto"}
    except Exception as e:
        logger.error(f"Erro ao mover mouse: {e}")
        return {"status": "error", "message": str(e)}


def click_mouse(button: str = "left", clicks: int = 1) -> dict:
    """Clica com o mouse (left, right, middle)."""
    try:
        if sys.platform == "win32":
            script = f"""
import pyautogui
pyautogui.click(button='{button}', clicks={clicks})
print('Clique {button} x{clicks}')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {"status": "ok", "message": f"Clique {button} x{clicks}", "output": result.stdout}
        else:
            return {"status": "error", "message": "Mouse control só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao clicar: {e}")
        return {"status": "error", "message": str(e)}


def type_text(text: str, interval: float = 0.05) -> dict:
    """Digita texto no teclado."""
    try:
        if sys.platform == "win32":
            # Escapar caracteres especiais
            text_escaped = text.replace("'", "\\'").replace('"', '\\"')
            script = f"""
import pyautogui
import time
pyautogui.typewrite(r'{text_escaped}', interval={interval})
print('Texto digitado: {len(text)} caracteres')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {"status": "ok", "message": f"Digitado: {text[:50]}", "output": result.stdout}
        else:
            return {"status": "error", "message": "Keyboard control só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao digitar: {e}")
        return {"status": "error", "message": str(e)}


def press_key(key: str) -> dict:
    """Pressiona uma tecla (enter, space, tab, esc, etc.)."""
    try:
        if sys.platform == "win32":
            script = f"""
import pyautogui
pyautogui.press('{key}')
print('Tecla pressionada: {key}')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {"status": "ok", "message": f"Tecla: {key}", "output": result.stdout}
        else:
            return {"status": "error", "message": "Keyboard control só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao pressionar tecla: {e}")
        return {"status": "error", "message": str(e)}


def hotkey(keys: list) -> dict:
    """Pressiona combinação de teclas (ex: ['ctrl', 'c'])."""
    try:
        if sys.platform == "win32":
            keys_str = "', '".join(keys)
            script = f"""
import pyautogui
pyautogui.hotkey('{keys_str}')
print('Atalho: {' + '.join(keys)}')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {"status": "ok", "message": f"Atalho: {'+'.join(keys)}", "output": result.stdout}
        else:
            return {"status": "error", "message": "Keyboard control só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao usar hotkey: {e}")
        return {"status": "error", "message": str(e)}


def get_mouse_position() -> dict:
    """Retorna posição atual do mouse."""
    try:
        if sys.platform == "win32":
            script = """
import pyautogui
x, y = pyautogui.position()
print(f'{x},{y}')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            x, y = result.stdout.strip().split(",")
            return {"status": "ok", "x": int(x), "y": int(y)}
        else:
            return {"status": "error", "message": "Mouse control só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao obter posição: {e}")
        return {"status": "error", "message": str(e)}


def screenshot_save(path: str = "screenshot.png") -> dict:
    """Tira screenshot e salva."""
    try:
        if sys.platform == "win32":
            script = f"""
import pyautogui
img = pyautogui.screenshot()
img.save(r'{path}')
print('Screenshot salvo: {path}')
"""
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return {"status": "ok", "message": f"Screenshot salvo em {path}", "output": result.stdout}
        else:
            return {"status": "error", "message": "Screenshot só suporta Windows"}
    except Exception as e:
        logger.error(f"Erro ao tirar screenshot: {e}")
        return {"status": "error", "message": str(e)}


def execute_mouse_keyboard_action(action: str, params: dict) -> dict:
    """Executor principal de ações de mouse/teclado."""
    
    mapa = {
        "move_mouse": lambda: move_mouse(params.get("x", 0), params.get("y", 0)),
        "click": lambda: click_mouse(params.get("button", "left"), params.get("clicks", 1)),
        "type": lambda: type_text(params.get("text", ""), params.get("interval", 0.05)),
        "press_key": lambda: press_key(params.get("key", "enter")),
        "hotkey": lambda: hotkey(params.get("keys", ["ctrl", "c"])),
        "get_position": lambda: get_mouse_position(),
        "screenshot": lambda: screenshot_save(params.get("path", "screenshot.png")),
    }
    
    fn = mapa.get(action)
    if fn:
        return fn()
    else:
        return {"status": "error", "message": f"Ação desconhecida: {action}"}
