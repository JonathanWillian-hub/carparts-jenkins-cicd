#!/usr/bin/env bash
# Executar somente após revisar os custos e autorizar criação na sua Azure.
set -euo pipefail
set +x
: "${AZURE_SUBSCRIPTION_ID:?}" "${ACR_NAME:?Escolha nome global único}"
AZURE_RG=${AZURE_RG:-rg-carparts-cicd}
LOCATION=${LOCATION:-eastus}
HOM_APP=${HOM_APP:-carparts-hom}
PROD_APP=${PROD_APP:-carparts-prod}
[[ "$ACR_NAME" =~ ^[a-z0-9]{5,50}$ ]]
az account set --subscription "$AZURE_SUBSCRIPTION_ID"
az extension add --name containerapp --upgrade --only-show-errors
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az group create --name "$AZURE_RG" --location "$LOCATION" --output none
az acr create --name "$ACR_NAME" --resource-group "$AZURE_RG" --sku Basic --admin-enabled false --output none
az containerapp env create --name carparts-env --resource-group "$AZURE_RG" --location "$LOCATION" --output none
registry_id=$(az acr show --name "$ACR_NAME" --resource-group "$AZURE_RG" --query id -o tsv)
for app in "$HOM_APP" "$PROD_APP"; do
  az containerapp create --name "$app" --resource-group "$AZURE_RG" --environment carparts-env \
    --image mcr.microsoft.com/k8se/quickstart:latest --target-port 80 --ingress external \
    --cpu 0.25 --memory 0.5Gi --min-replicas 0 --max-replicas 1 --system-assigned --output none
  principal=$(az containerapp show --name "$app" --resource-group "$AZURE_RG" --query identity.principalId -o tsv)
  az role assignment create --assignee-object-id "$principal" --assignee-principal-type ServicePrincipal \
    --role AcrPull --scope "$registry_id" --output none
  az containerapp registry set --name "$app" --resource-group "$AZURE_RG" \
    --server "$ACR_NAME.azurecr.io" --identity system --output none
  az containerapp update --name "$app" --resource-group "$AZURE_RG" --revision-mode single --output none
  az containerapp ingress update --name "$app" --resource-group "$AZURE_RG" --transport auto --allow-insecure false --output none
done
printf 'Recursos criados. Configure RBAC do service principal e credenciais Jenkins antes de executar release.\n'
