# E6 · Métricas, melhoria e custo

| Métrica | Definição no laboratório | Fonte |
|---|---|---|
| Lead time | Deploy em produção validado menos timestamp do commit | `commitEpoch` e `deployedAt` |
| Frequência | Releases bem-sucedidas por dia da janela | `productionSucceeded` |
| Taxa de falha | Tentativas de produção com falha / tentativas × 100 | flags `productionAttempted/Failed` |

O calculador `metrics/summarize.py` exige pelo menos 10 `run.json` reais, URLs únicas, ordem temporal válida, aprovação e imagem por digest nos sucessos. Falhas de CI não contam como falha de mudança. A baseline fornecida é 11 dias = 264h; a meta é 2 dias = 48h, redução necessária de 81,82%. Frequência e taxa de falha iniciais não foram fornecidas e devem ser medidas.

## Plano de oito semanas

| Período | Ação e critério |
|---|---|
| 1 | Controller JCasC, agentes, backup/restauração; confirmar 0 executores internos |
| 2 | CI automática por PR e JUnit; falha bloqueia merge |
| 3 | Construção única e ACR por digest verificável |
| 4 | Homologação, smoke e primeiras 10 execuções |
| 5 | Aprovação registrada; fila inferior a 4 horas úteis |
| 6 | Exercício de rollback por digest em até 30 minutos |
| 7 | Medir fila/teste/aprovação e reduzir lotes |
| 8 | Comparar janela final com 264h e meta 48h |

## Orçamento mensal planejado

Premissas: East US, ACR Basic, duas Container Apps Consumption de 0,25 vCPU/0,5 GiB, min 0/max 1, pouco tráfego e sem VM/AKS.

| Item | Reserva USD |
|---|---:|
| ACR Basic | 10 |
| Container Apps | 25 |
| Logs/retenção | 10 |
| Tráfego/armazenamento excedente | 10 |
| Contingência | 20 |
| **Total planejado** | **75** |

A reserva de US$75 fica abaixo do teto de US$150, mas não é cotação/fatura. Validar região, oferta e consumo na Azure Pricing Calculator e Cost Management; criar alertas em US$75, US$100 e US$135. Orçamento não bloqueia cobrança automaticamente.

Fontes: https://learn.microsoft.com/en-us/azure/container-apps/billing, https://azure.microsoft.com/en-us/pricing/details/container-apps/, https://azure.microsoft.com/en-us/pricing/details/container-registry/, https://azure.microsoft.com/en-us/pricing/calculator/.
