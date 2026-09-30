# PR de exemplo · validação do fluxo Git

Este arquivo registra o teste do fluxo por pull request exigido no E5.

- Mudança: adicionar evidência documental sem alterar a aplicação.
- Validação esperada: GitHub Action “Validar projeto Carparts”.
- Critério de aceite: jobs “Aplicacao e seguranca” e “Controller Jenkins e linter” concluídos com sucesso.
- Relação com a atividade: demonstra pipeline por PR e fornece o nome exato dos checks para configurar a proteção da branch `main`.

O webhook Jenkins e a proteção de branch ainda devem ser configurados no ambiente real conforme `docs/E5-github.md`.
