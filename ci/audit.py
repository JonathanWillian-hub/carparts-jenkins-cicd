#!/usr/bin/env python3
"""Auditoria preventiva; não substitui revisão de histórico/logs e secret scanning."""
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
errors = []
patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{40,}', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'AKIA[A-Z0-9]{16}']
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('.git', 'node_modules', 'secrets', '__pycache__')):
        continue
    if p.name == 'audit.py': continue
    try: text = p.read_text()
    except UnicodeDecodeError: continue
    if any(re.search(pattern, text) for pattern in patterns): errors.append(str(p.relative_to(root)) + ': possível segredo')
casc = (root / 'jenkins/casc.yaml').read_text()
compose = (root / 'compose.yaml').read_text()
pipeline = (root / 'Jenkinsfile').read_text()
if not re.search(r'jenkins:\s.*?numExecutors: 0', casc, re.S): errors.append('Controller deve ter 0 executores')
if 'allowsSignup: false' not in casc or 'Overall/Read:anonymous' in casc: errors.append('Revisar autenticação')
if '127.0.0.1:8080:8080' not in compose: errors.append('8080 precisa estar restrita a loopback')
if '/var/run/docker.sock' in compose: errors.append('Controller não pode receber socket Docker')
for item in ('agent none', 'junit ', 'timeout(', 'submitterParameter:', 'approval.json', "branch 'main'", 'post {'):
    if item not in pipeline: errors.append('Pipeline sem ' + item)
if pipeline.count('docker build ') != 1: errors.append('Exigir construção única da imagem')
if errors:
    for error in errors: print('FAIL:', error)
    raise SystemExit(1)
print('PASS: padrões conhecidos de segredos e invariantes estáticos verificados; execução Azure exige evidência real.')
