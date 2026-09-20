# -*- coding: utf-8 -*-
"""API endpoints para controle de mouse e teclado."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mouse_keyboard_control import execute_mouse_keyboard_action

router = APIRouter(prefix="/api/mouse_keyboard", tags=["mouse_keyboard"])


class MouseKeyboardRequest(BaseModel):
    action: str
    params: dict = {}


@router.post("/execute")
async def execute_action(req: MouseKeyboardRequest):
    """Execute uma ação de mouse ou teclado."""
    try:
        result = execute_mouse_keyboard_action(req.action, req.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/position")
async def get_position():
    """Get current mouse position."""
    return execute_mouse_keyboard_action("get_position", {})


@router.post("/move")
async def move(x: int, y: int):
    """Move mouse to coordinates."""
    return execute_mouse_keyboard_action("move_mouse", {"x": x, "y": y})


@router.post("/click")
async def click(button: str = "left", clicks: int = 1):
    """Click mouse."""
    return execute_mouse_keyboard_action("click", {"button": button, "clicks": clicks})


@router.post("/type")
async def type_text(text: str, interval: float = 0.05):
    """Type text."""
    return execute_mouse_keyboard_action("type", {"text": text, "interval": interval})


@router.post("/key")
async def press_key(key: str):
    """Press a key."""
    return execute_mouse_keyboard_action("press_key", {"key": key})


@router.post("/screenshot")
async def screenshot(path: str = "screenshot.png"):
    """Take screenshot."""
    return execute_mouse_keyboard_action("screenshot", {"path": path})
