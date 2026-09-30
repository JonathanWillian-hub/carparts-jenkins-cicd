#!/usr/bin/env bash
# Criar a aplicação e segredo pela interface Entra; não imprimir segredo via CLI.
set -euo pipefail
set +x
: "${AZURE_SUBSCRIPTION_ID:?}" "${AZURE_RG:?}" "${ACR_NAME:?}" "${SP_OBJECT_ID:?Object ID do service principal}"
rg_scope="/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RG"
registry_id=$(az acr show --name "$ACR_NAME" --resource-group "$AZURE_RG" --query id -o tsv)
az role assignment create --assignee-object-id "$SP_OBJECT_ID" --assignee-principal-type ServicePrincipal \
  --role 'Container Apps Contributor' --scope "$rg_scope" --output none
az role assignment create --assignee-object-id "$SP_OBJECT_ID" --assignee-principal-type ServicePrincipal \
  --role AcrPush --scope "$registry_id" --output none
printf 'RBAC aplicado ao grupo e ao ACR. Sem papel na assinatura inteira.\n'
