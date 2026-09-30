# Checklist eliminatório

**Estado atual: código publicado; evidências de infraestrutura ainda pendentes.**

| Critério eliminatório | Controle | Evidência necessária |
|---|---|---|
| Segredo no repo/log | ignore, Docker secrets, cofre Jenkins, CLI silenciosa | Revisão completa de histórico, logs e prints |
| Build no controller | 0 executores, agent none, agentes nomeados | Print do nó e log “Running on” |
| Jenkins público/inseguro | loopback, autenticação, 50000 desativada | Firewall/proxy e acesso anônimo negado |
| Produção sem aprovação/rebuild | approval.json e promoção do mesmo digest | Ordem temporal e igualdade de digest |
| Sem execução real | automação + roteiro | Jenkins/Azure/webhook e 10 runs reais |

- [ ] RA preenchido.
- [ ] Action verde e artefatos de validação baixados.
- [ ] Controller real iniciou, login exigido, 0 executores internos e agentes online.
- [ ] JUnit publicado; `when`, `timeout` e `post` visíveis.
- [ ] RBAC Azure limitado, credenciais no cofre, homologação e smoke reais.
- [ ] Aprovação por `release-manager` precede produção; digest é idêntico.
- [ ] Webhook 2xx, Multibranch, check no PR e main protegida.
- [ ] 10+ `run.json`, resumo DORA e comparação com 11 dias.
- [ ] Custo validado dentro de US$150.
- [ ] Logs e capturas revisados; nenhum segredo ou dado de outro grupo.
