#!/usr/bin/env bash
# Recuperação técnica acionada pelo deploy já aprovado; não constrói imagem.
set -euo pipefail
set +x
: "${AZURE_RG:?}" "${PROD_APP:?}"
previous=${1:?Digest anterior necessário}
[[ "$previous" =~ ^[a-z0-9]+\.azurecr\.io/carparts@sha256:[a-f0-9]{64}$ ]] || { echo 'Rollback precisa de release anterior por digest'; exit 1; }
az containerapp update --name "$PROD_APP" --resource-group "$AZURE_RG" --image "$previous" --output none --only-show-errors
printf 'Recuperação solicitada para digest anterior. Validar /health e registrar incidente.\n'
