#!/usr/bin/env bash
set -euo pipefail
set +x
mode=${1:?Use hom ou prod}
image=${2:?Informe imagem por digest}
[[ "$mode" == hom || "$mode" == prod ]]
[[ "$image" =~ ^[a-z0-9]+\.azurecr\.io/carparts@sha256:[a-f0-9]{64}$ ]] || { echo 'Imagem precisa usar digest ACR'; exit 1; }
: "${AZURE_RG:?}" "${HOM_APP:?}" "${PROD_APP:?}" "${RELEASE_COMMIT:?}"
app=$HOM_APP
[[ "$mode" != prod ]] || app=$PROD_APP
if [[ "$mode" == prod ]]; then
  [[ -s approval.json ]] || { echo 'Aprovação ausente'; exit 1; }
  node ci/verify-approval.mjs approval.json "$image" "$RELEASE_COMMIT"
fi
previous=''
if [[ "$mode" == prod ]]; then
  previous=$(az containerapp show --name "$app" --resource-group "$AZURE_RG" --query 'properties.template.containers[0].image' -o tsv --only-show-errors)
fi
recover() {
  status=$?
  trap - ERR
  if [[ "$mode" == prod && "$previous" =~ /carparts@sha256:[a-f0-9]{64}$ ]]; then
    bash ci/rollback.sh "$previous" || echo 'Recuperação falhou: intervenção necessária'
  elif [[ "$mode" == prod ]]; then
    echo 'Primeira release: sem versão Carparts anterior para recuperação automática'
  fi
  exit "$status"
}
trap recover ERR
az containerapp ingress update --name "$app" --resource-group "$AZURE_RG" --target-port 3000 --output none --only-show-errors
az containerapp update --name "$app" --resource-group "$AZURE_RG" --image "$image" --output none --only-show-errors
fqdn=$(az containerapp show --name "$app" --resource-group "$AZURE_RG" --query properties.configuration.ingress.fqdn -o tsv --only-show-errors)
node ci/smoke.mjs "https://$fqdn" "$RELEASE_COMMIT"
