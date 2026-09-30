# Relatório · SAP1-DEVOPS Carparts

**Aluno:** Jonathan Willian de Paula Santos  
**RA:** preencher antes da entrega

## E1 · Arquitetura

O controller Jenkins será executado localmente em Docker, com zero executores, autenticação obrigatória e persistência. Dois agentes Ubuntu separados executam CI e release. O diagrama documenta sistemas operacionais, rótulos, executores, portas, Azure, alternativas, custo e riscos.

## E2 · Controller reproduzível

A imagem fixa Jenkins LTS com Java 21, instala plugins por arquivo e aplica JCasC. Senhas entram por Docker secrets, cadastro anônimo fica desativado, a porta 8080 permanece em loopback, a porta de agentes TCP é desativada e o controller não recebe Docker socket.

## E3 · Jenkinsfile

O pipeline executa checkout, qualidade paralela, testes JUnit, construção única, publicação no ACR, homologação, smoke, aprovação e produção. `when` limita release à main, `timeout` evita espera infinita, `post` registra o resultado e a aprovação ocorre sem ocupar executor.

## E4 · Azure

Scripts criam ACR Basic e Container Apps com escala a zero. O service principal recebe apenas Container Apps Contributor no grupo e AcrPush no ACR. Apps usam identidade gerenciada para pull. O deploy promove o mesmo digest e aciona recuperação anterior se o smoke de produção falhar.

## E5 · Multibranch e webhook

CI de branch/PR fica numa pasta sem segredos; release descobre apenas main e guarda credenciais Azure em escopo local. O roteiro exige webhook assinado, status no GitHub, ruleset de main, check verde obrigatório e PR comentado com evidência real.

## E6 · Métricas e melhoria

Cada build de release arquiva `run.json`. O agregador exige 10 ou mais execuções reais e calcula lead time, frequência e taxa de falha. A baseline de 11 dias é comparada à meta de 2 dias; o plano de oito semanas e orçamento estimado de US$75 orientam a melhoria.

## Evidências

A validação automática do repositório comprova aplicação, imagem local, regras estáticas e controller efêmero. Prints/logs do Jenkins real, Azure, webhook, PR protegido e 10 execuções devem ser anexados após seguir `EXECUTAR.md`. Essa distinção impede apresentar simulação como execução.
