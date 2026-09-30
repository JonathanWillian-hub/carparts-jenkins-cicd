# SAP1-DEVOPS · Carparts · Jenkins e Azure

**Aluno:** Jonathan Willian de Paula Santos  
**RA:** preencher antes da entrega

Projeto acadêmico completo para adoção do Jenkins como servidor CI/CD do portal B2B da Carparts, com controller autogerenciado local, agentes separados, Azure Container Registry, homologação e produção acadêmica em Azure Container Apps.

> **Estado auditável:** código e validações automatizadas publicados. A execução do Jenkins, o deploy Azure, o webhook, a aprovação e as 10 execuções reais dependem da infraestrutura do aluno. Não enviar como atividade concluída enquanto o checklist estiver pendente.

## Entregáveis

| Item | Implementação |
|---|---|
| E1 · Arquitetura | [Diagrama, agentes, executores, rótulos, portas, custos e riscos](docs/E1-arquitetura.md) |
| E2 · Controller reproduzível | `jenkins/Dockerfile`, `plugins.txt`, `casc.yaml`, `compose.yaml`; nó interno com 0 executores, cadastro fechado e porta 8080 em loopback |
| E3 · Jenkinsfile CI/CD | Qualidade, testes JUnit, imagem, ACR, homologação, smoke, aprovação e produção; `when`, `timeout` e `post` |
| E4 · Azure | RBAC limitado, login seguro, Container Apps, ACR, identidade gerenciada para pull, smoke e recuperação por digest |
| E5 · Multibranch + webhook | CI de branches/PRs separada do job release e [roteiro de GitHub](docs/E5-github.md) |
| E6 · Métricas e melhoria | Coletor que exige 10+ execuções reais, metas, plano de oito semanas e [orçamento](docs/E6-metricas-custos.md) |

Consulte [o relatório da atividade](docs/RELATORIO.md), [o roteiro de execução](docs/EXECUTAR.md) e [o checklist eliminatório](docs/ENTREGA.md).

## Validação automática

A GitHub Action executa testes da aplicação, verificador de aprovação, calculador de métricas, auditoria preventiva de segredos, build/smoke da imagem e subida efêmera do Jenkins. Ela também comprova que o controller bloqueia acesso anônimo, possui 0 executores internos e aceita a sintaxe dos Jenkinsfiles.

Essas verificações não simulam deploy Azure nem criam evidências falsas. E4, E5 e E6 só ficam completos depois das execuções reais descritas no roteiro.

## Teste local

```bash
python3 ci/audit.py
cd app
npm ci --ignore-scripts --no-audit --no-fund
npm run lint
npm test
cd ..
node --test ci/test/*.test.mjs
python3 ci/test/metrics_test.py
```

## Controles contra nota zero

- Nenhum segredo no repositório; JCasC lê Docker secrets e Jenkins injeta credenciais por IDs.
- Controller com `numExecutors: 0`, sem Docker socket e sem porta 50000.
- Porta 8080 ligada somente a `127.0.0.1`; acesso anônimo bloqueado.
- Imagem construída uma vez e promovida pelo mesmo digest.
- Produção exige `approval.json` com usuário, data, commit, digest e URL do build.
- Métricas recusam menos de 10 execuções ou artefatos duplicados/inconsistentes.
- Evidências pendentes são declaradas; nenhum print ou log foi inventado.

Fontes oficiais e premissas constam nos documentos do projeto.
