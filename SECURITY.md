# Integridade e publicação

O site é estático. Seu HTML, CSS, JavaScript e imagens são enviados ao navegador e, portanto, não podem ser criptografados de forma que o visitante execute o código sem poder inspecioná-lo. Ofuscação e lógica que quebra a página quando alguém remove a assinatura não protegem a autoria e podem causar indisponibilidade.

## Controles implementados

- A homepage declara CSP restritiva para scripts e estilos do próprio domínio, imagens da BDM, iframe do YouTube somente após clique e ausência de conexões iniciadas pelo site. No GitHub Pages, a política é aplicada por `meta`, sem substituir cabeçalhos HTTP de um servidor controlado.
- `integrity` com SHA-384 no stylesheet e no módulo JS de entrada impede que esses arquivos alterados sejam executados sem atualizar o HTML. Os módulos importados permanecem sob `script-src 'self'` e são conferidos pelo manifesto SHA-256 durante a validação.
- `integrity.sha256` cobre o HTML, código modular e imagens da hero. A GitHub Action falha se o bundle CSS, as referências, a assinatura ou os hashes não conferirem.
- `CODEOWNERS` registra `@emeverton` como responsável pela revisão. Para exigir sua aprovação antes de merges, habilite proteção da branch e marque `Verify site integrity` como check obrigatório nas configurações do repositório.

Esses controles detectam mudanças acidentais ou não revisadas. Alguém com permissão de escrita irrestrita pode alterar o código e o manifesto no mesmo commit. Proteção de branch, revisão obrigatória e controle de acesso à conta GitHub são necessários para resistir a esse cenário. O site deve continuar disponível enquanto uma alteração é investigada.

## Mudança autorizada

1. Edite os arquivos em `styles/` e `modules/`, não o bundle CSS manualmente.
2. Execute `python3 scripts/build_css.py`.
3. Execute `python3 scripts/update_sri.py` quando `styles.css` ou `app.js` mudarem.
4. Execute `python3 scripts/integrity.py --write`, revise o diff e rode os checks do README.
