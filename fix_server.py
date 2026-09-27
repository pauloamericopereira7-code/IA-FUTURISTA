#!/usr/bin/env python3
# Script para atualizar server.py
import os
os.chdir('futurista')
content = open('server.py', 'r', encoding='utf-8').read()

# Adicionar import do multiagent
if 'from api_multiagent' not in content:
    content = content.replace(
        'from api_mouse_keyboard import router as mouse_keyboard_router\n',
        'from api_mouse_keyboard import router as mouse_keyboard_router\nfrom api_multiagent import router as multiagent_router\n'
    )

# Adicionar include_router
if 'include_router(multiagent_router)' not in content:
    content = content.replace(
        'app.include_router(mouse_keyboard_router)\n',
        'app.include_router(mouse_keyboard_router)\napp.include_router(multiagent_router)\n'
    )

# Servir a interface multiagent
content = content.replace(
    '@app.get("/")\nasync def root():\n    return FileResponse(STATIC / "index.html")',
    '@app.get("/")\nasync def root():\n    novo = STATIC / "index_multiagent.html"\n    if novo.exists():\n        return FileResponse(novo)\n    return FileResponse(STATIC / "index.html")'
)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("OK")
