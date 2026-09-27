# BDM Performance

Landing page estática, responsiva e sem dependências de runtime. O objetivo é explicar o modelo de parceria, qualificar a conversa e encaminhar o visitante para a equipe BDM.

## Conteúdo e identidade

- Logo, cores e campanhas foram derivados do pacote original da BDM Performance.
- O verde `#00AB58` foi amostrado do logo original. Grafite e neutros completam a paleta.
- Montserrat foi extraída do pacote de fontes recebido e subsetada para português e latim.
- O foco comercial é a conversa sobre parceria, retaguarda técnica e reprogramação eletrônica para a operação e a região do interessado.
- A página contempla oficinas, representantes regionais, frotas, agronegócio e entusiastas, com CTAs contextualizados.
- A comunicação evita números de resultado, garantias e condições comerciais que não estejam confirmados nos materiais.

## Contato e dados

- Os CTAs abrem o WhatsApp BDM `+55 44 98801-8242` com contexto pré-preenchido.
- Não há formulário, CRM, pixel, cookies de publicidade ou armazenamento de dados neste site.
- O número do WhatsApp é o contato informado no site da BDM.

## Estrutura

- `index.html`: landing page pública.
- `styles.css`: tokens, reset, estilos base, layout, componentes, rotas auxiliares e breakpoints.
- `app.js`: navegação mobile acessível e ano do rodapé.
- `assets/`: logo, campanhas convertidas em WebP e fontes locais.
- `brand/`, `ads/` e `review/`: páginas auxiliares `noindex,nofollow`.

## Validação

```sh
node --check app.js
python3 scripts/validate.py
python3 scripts/smoke.py
```

`validate.py` verifica estrutura, indexabilidade, referências locais, ativos, tokens de marca, foco de teclado, movimento reduzido e envio de dados. `smoke.py` verifica as rotas e os ativos publicados.

## Publicação

`main` é a fonte de trabalho e `gh-pages` publica o site. Promover alterações com fast-forward depois de validar; não usar force push.
