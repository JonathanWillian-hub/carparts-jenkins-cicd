# E5 · Multibranch, webhook e proteção da main

1. Criar pasta Jenkins `ci` sem credenciais de produção. Nela, criar Multibranch Pipeline com GitHub Branch Source e `Jenkinsfile.ci`, descobrindo branches e PRs da origem.
2. Criar pasta `release` com credenciais Azure locais à pasta. O Multibranch usa `Jenkinsfile`, descobre somente `main` e não executa PR/fork.
3. Usar GitHub App restrita a este repositório. Não confiar em forks externos nem permitir que PRs acessem agentes/segredos de release.
4. Configurar webhook HTTPS com segredo HMAC e eventos push/pull request. O proxy deve encaminhar somente POST para `/github-webhook/`; a UI Jenkins permanece privada.
5. Depois do primeiro build, copiar o nome exato do check produzido. Criar ruleset da `main` exigindo PR, check verde, resolução de conversas e bloqueio de force push/exclusão.
6. Criar PR de exemplo com alteração documental, registrar link do build e demonstrar bloqueio com status vermelho e liberação após correção.

Evidências: visão Multibranch, delivery 2xx sem segredo, PR e check, ruleset ativo e log disparado pelo evento. Scan manual ou `pollSCM` não concluem E5.

**Estado atual:** arquivos preparados; webhook, ruleset e PR dependem do Jenkins acessível e ainda precisam de execução real.
