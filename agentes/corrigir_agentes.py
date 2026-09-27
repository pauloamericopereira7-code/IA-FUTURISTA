#!/usr/bin/env python3
# Script para corrigir assinatura Mensagem em todos os agentes

import os
import glob

pattern = "agente_*.py"
folder = "."

for file in glob.glob(pattern):
    print(f"Corrigindo {file}...")
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir Mensagem(..., agente=...) por Mensagem(..., origem=...)
    content = content.replace(
        "Mensagem(\n            agente=self.nome,",
        "Mensagem(\n            origem=self.nome,"
    )
    content = content.replace(
        "agente=self.nome,",
        "origem=self.nome,"
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Correcao concluida!")
