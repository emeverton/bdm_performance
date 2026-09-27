# BDM Performance · V4 / Veltrus

Site estático de revisão da BDM Performance. Sem dependências de runtime.

## Publicação

GitHub Pages foi ativado usando a branch `gh-pages`, pasta raiz. O workflow nativo **pages build and deployment** publica o conteúdo dessa branch. `main` guarda o código de trabalho.

Para uma próxima publicação, validar o commit e atualizar `gh-pages` por fast-forward a partir de `main`. Não usar force push. Não presumir publicação a partir de um commit em `main`.

O workflow `BDM review checks` valida a fonte e, após o deploy nativo do Pages, verifica as quatro rotas HTTPS, CSS, JavaScript e checksums das imagens. Essas verificações não substituem auditoria visual nem medição de Core Web Vitals.

## Escopo

- Landing page responsiva e rotas `brand/`, `ads/`, `review/`.
- Hero selecionada na conversa, otimizada para AVIF sem corte.
- Logo fornecido no projeto, convertido para WebP.
- `noindex,nofollow` em todas as páginas de revisão. O site é público; noindex não é controle de acesso.
- Formulário demonstrativo sem backend, sem envio de contatos e sem conversão real.
- Brand e Ads são bases para revisão, não manual ou peças finais aprovados.

A hero é imagem conceitual gerada por IA e contém texto incorporado. Ela não comprova instalações, veículos de clientes ou resultados reais da BDM. A revisão visual é obrigatória antes do uso comercial.

## Execução local

```sh
python3 scripts/validate.py
node --check app.js
python3 -m http.server 8080
```

Acesse `http://localhost:8080/`.

## Gate comercial

Aprovar identidade e peças; validar claims e provas; definir política de privacidade e destino do atendimento; conectar backend; disparar conversão somente após confirmação de sucesso; verificar acessibilidade, mobile e Core Web Vitals.

Não adicionar segredos, tokens, dados pessoais, exportações do CRM ou documentos internos do Drive a este repositório público. As tasks do eKyte continuam aguardando revisão humana.
