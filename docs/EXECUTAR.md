# Roteiro para gerar as evidências reais

## 1. Controller

No clone local, criar senhas sem imprimi-las:

```bash
mkdir -p secrets
python3 - <<'PY'
from pathlib import Path
from getpass import getpass
for name in ('admin_password','approver_password'):
    value=getpass('Senha longa para '+name+': ')
    if len(value)<16: raise SystemExit('Use pelo menos 16 caracteres')
    p=Path('secrets')/name; p.write_text(value); p.chmod(0o600)
PY
docker compose build --no-cache
docker compose up -d
```

Abrir `http://localhost:8080`, confirmar login obrigatório, Built-In Node com 0 executores e agentes configurados. Nunca versionar `secrets/` ou logs sem revisão.

## 2. Agentes

Usar Java 21 e conta de serviço sem root. O agente CI recebe Node/Python/Git; o release também recebe Docker e Azure CLI. Conectar por WebSocket através de rede privada ou túnel SSH. Guardar segredo do agente em arquivo privado e usar `-secret @arquivo`. Rótulos não substituem controle de autorização; reservar release para o job autorizado.

## 3. Azure

Revisar custos e entrar com `az login` na estação administrativa:

```bash
export AZURE_SUBSCRIPTION_ID='ID'
export AZURE_RG='rg-carparts-cicd'
export ACR_NAME='nomeglobalunico'
export LOCATION='eastus'
bash infra/provision.sh
```

Criar aplicação exclusiva no Entra e copiar o segredo diretamente para o cofre Jenkins. Informar `SP_OBJECT_ID` e executar `infra/rbac.sh`. Cadastrar IDs Jenkins: `azure-sp` (username/password), `azure-tenant` e `azure-subscription` (secret text), todos apenas na pasta release.

## 4. Jobs e GitHub

Seguir `E5-github.md`. Parametrizar RG, ACR e nomes dos apps no job release. Primeiro validar PR/CI; depois executar main, conferir homologação e entrar como `release-manager` para aprovar. Arquivar JUnit, `image-ref.txt`, `approval.json`, `run.json` e logs sanitizados.

## 5. Dez execuções

Executar pelo menos 10 builds reais. Baixar cada `run.json` para `metrics/downloads/build-N/` e calcular:

```bash
python3 metrics/summarize.py metrics/downloads \
  --start 'DATA_REAL_COM_FUSO' --end 'DATA_REAL_COM_FUSO' > metrics/summary.json
```

Associar cada artefato ao build e atualizar o relatório com os números reais. Não provocar falha em produção real; falhas autênticas de laboratório podem ser registradas.

## 6. Encerramento

Aplicar `ENTREGA.md`, preencher RA e links, validar custo real, revisar histórico/logs/prints por segredos e remover recursos Azure pelo portal quando terminar.
