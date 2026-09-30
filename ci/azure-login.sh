#!/usr/bin/env bash
set -euo pipefail
set +x
: "${AZURE_CLIENT_ID:?Credencial Jenkins ausente}" "${AZURE_CLIENT_SECRET:?Credencial Jenkins ausente}"
: "${AZURE_TENANT_ID:?Credencial Jenkins ausente}" "${AZURE_SUBSCRIPTION_ID:?Configuração ausente}"
az login --service-principal --username "$AZURE_CLIENT_ID" --password "$AZURE_CLIENT_SECRET" --tenant "$AZURE_TENANT_ID" --output none --only-show-errors
az account set --subscription "$AZURE_SUBSCRIPTION_ID"
