# BDM Performance · site de revisão

Site estático, responsivo e sem dependências de runtime. A identidade visual foi refeita a partir do pacote original BDM Performance recebido em 27/09/2026.

## Fontes consultadas

- `3. Conteúdos Cliente/logo bdm alta def.png`, logo colorido original.
- `3. Conteúdos Cliente/Arquitetura da marca-BDM-aumentada.pdf` e `.eps`.
- `4. Conteúdos V4/Relatórios Social Media/BDM - Análise de Design e Usabilidade.docx`.
- `4. Conteúdos V4/Relatórios Social Media/BDM - Anotações reunião.docx`.
- `4. Conteúdos V4/Relatórios Social Media/BDM - Manual de copy.docx`.
- Criativos originais da pasta `3. Conteúdos Cliente`, convertidos para WebP sem criação de novas cenas.

## Identidade aplicada

O verde primário `#00AB58` foi amostrado do logo colorido original. O grafite foi amostrado do lettering. A análise de design da V4 descreve a combinação verde, preto e neutros e recomenda usar o verde com hierarquia. Tons adicionais no CSS são tratamentos de interface, não cores oficiais declaradas pelo cliente. Vermelho não é usado como cor proprietária.

## Escopo e limites

- Landing page e rotas `brand/`, `ads/` e `review/`.
- Público priorizado: oficinas, representantes e operações ligadas a frotas e agronegócio, conforme os materiais recebidos.
- Cenas conceituais geradas por IA removidas e substituídas por peças originais do cliente.
- Sem formulário, backend, transmissão de dados ou eventos de conversão.
- `noindex,nofollow` mantido em todas as rotas, pois este é um ambiente de revisão pública.
- Copy, oferta atual, canal de atendimento, política de privacidade, tracking e aprovação comercial ainda dependem do cliente.
- Não foram publicados PDFs, documentos internos ou arquivos pessoais no repositório público.

As anotações de reunião pedem retirar claims de exclusividade de software, e o projeto evita também garantias de potência, economia e retrabalho zero. Não transformar conteúdo conceitual em alegação de resultado.

## Validação local

```sh
python3 scripts/validate.py
node --check app.js
python3 -m http.server 8080
```

## Publicação

`main` é a fonte de trabalho. GitHub Pages publica a branch `gh-pages`. Promover alterações com fast-forward após os checks; não usar force push. A publicação continua em `noindex,nofollow` até aprovação comercial.
