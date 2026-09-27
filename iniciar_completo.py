#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRAÇÃO COMPLETA: IA Futurista + Multiagente + Interface Web
=================================================================
Este script integra TUDO em uma única interface moderna.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  🤖 IA FUTURISTA - SISTEMA MULTIAGENTE                  ║
    ║  Iniciando integração completa...                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 1. Checar Docker
    print("1️⃣  Verificando Docker...")
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        print("   ✅ Docker OK")
    except:
        print("   ❌ Docker não encontrado. Instale Docker Desktop.")
        sys.exit(1)
    
    # 2. Iniciar containers
    print("\n2️⃣  Iniciando containers Docker...")
    os.chdir(Path(__file__).parent)
    result = subprocess.run(["docker", "compose", "up", "-d"], capture_output=True)
    if result.returncode == 0:
        print("   ✅ Containers iniciados")
    else:
        print(f"   ❌ Erro ao iniciar Docker: {result.stderr.decode()}")
        sys.exit(1)
    
    # 3. Aguardar servidor
    print("\n3️⃣  Aguardando servidor inicializar...")
    time.sleep(3)
    for i in range(30):
        try:
            import requests
            resp = requests.get("http://localhost:8742/api/status", timeout=2)
            if resp.status_code == 200:
                print("   ✅ Servidor respondendo")
                break
        except:
            print(f"   Tentativa {i+1}/30...", end="\r")
            time.sleep(1)
    else:
        print("   ⚠️  Servidor demorando... Continue acessando http://localhost:8742")
    
    # 4. Abrir navegador
    print("\n4️⃣  Abrindo interface web...")
    time.sleep(1)
    
    try:
        import webbrowser
        webbrowser.open("http://localhost:8742")
        print("   ✅ Navegador aberto em http://localhost:8742")
    except:
        print("   ℹ️  Abra manualmente: http://localhost:8742")
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  🎉 IA FUTURISTA ONLINE!                                ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  🌐 Interface: http://localhost:8742                     ║
    ║  🤖 10 Agentes Especializados                            ║
    ║  💾 Cache Inteligente                                    ║
    ║  ⚙️  Automações Auditadas                                ║
    ║  🖱️  Controle de Mouse/Teclado                          ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Comandos úteis:
    - Parar: docker compose down
    - Logs: docker logs ia-futurista -f
    - Restart: docker compose restart
    """)

if __name__ == "__main__":
    main()
