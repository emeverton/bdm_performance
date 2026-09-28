# BDM Performance

Landing page estática, responsiva e sem dependências de runtime. O objetivo é explicar o modelo de parceria, qualificar a conversa e encaminhar o visitante para a equipe BDM.

## Conteúdo e identidade

- Logo, cores e campanhas foram derivados do pacote original da BDM Performance.
- O verde `#00AB58` foi amostrado do logo original. Grafite e neutros completam a paleta.
- Montserrat foi extraída do pacote de fontes recebido e subsetada para português e latim.
- O foco comercial é captar oficinas e profissionais comerciais para o modelo Ponto de Apoio. Clientes finais têm um funil separado.
- A seção de operação usa o modelo de leitura, programação e suporte descrito no site institucional da BDM. O portfólio de cada parceiro depende da avaliação comercial.
- Os depoimentos de Lucas Calciolari e Kevin Oliveira são vídeos publicados na página oficial do programa de autorizados da BDM. Eles documentam experiências anteriores e não representam condições contratuais do Ponto de Apoio atual.
- A tradição de mais de 30 anos pertence ao grupo Bombas Diesel Maringá, conforme página institucional. Números de revendedores, ganhos, retrabalho, payback, exclusividade e suporte 24/7 não são afirmados nesta landing page.

## Contato e dados

- Os CTAs abrem o WhatsApp BDM `+55 44 98801-8242` com contexto pré-preenchido. Quando a URL de entrada contém UTMs, `utm_source`, `utm_medium` e `utm_campaign` são acrescentadas à mensagem, sem identificadores pessoais ou click IDs.
- Os cliques em CTA emitem `bdm_partner_cta_click` em `window.dataLayer`, com seção e UTMs. Isso é apenas um hook para futura instalação de GTM. Ainda não existe coleta, pixel, CRM ou medição de conversa iniciada e parceiro qualificado neste site.
- Os vídeos do YouTube são carregados apenas após um clique; as imagens de capa dos depoimentos vêm da página oficial BDM. Não há formulário nem cookies de publicidade instalados pela página.
- O número do WhatsApp é o contato informado no site da BDM.

## Estrutura

- `index.html`: landing page pública.
- `styles/`: fontes de CSS divididas por tokens/base, componentes, páginas auxiliares e responsividade. `scripts/build_css.py` gera o único `styles.css` servido ao navegador.
- `modules/`: navegação mobile, depoimentos sob demanda e contexto de campanha nos CTAs. `app.js` é o módulo de entrada.
- `assets/`: logo, campanhas originais convertidas em WebP, fontes locais e a imagem ilustrativa da hero enviada para esta revisão. O master 8K mede 7680 × 4320, derivado por ampliação da imagem de 1672 × 941; não contém detalhe real equivalente a uma captura nativa 8K. O navegador escolhe entre 960, 1920, 3840 e 7680 pixels conforme tela e densidade. A cena não documenta uma instalação ou colaborador real da BDM.
- `brand/`, `ads/` e `review/`: páginas auxiliares `noindex,nofollow`.
- `SECURITY.md`, `integrity.sha256` e `.github/workflows/verify.yml`: política de segurança, hashes e validação automática.

## Validação

```sh
python3 scripts/build_css.py --check
python3 scripts/integrity.py
node --check app.js
node --check modules/navigation.js
node --check modules/testimonials.js
node --check modules/attribution.js
python3 scripts/validate.py
BDM_LOCAL_ROOT="$PWD" python3 scripts/smoke.py
```

`validate.py` verifica estrutura, indexabilidade, referências locais, hero, assinatura, CSP, SRI, marca, foco de teclado e envio de dados. `smoke.py` verifica rotas e ativos locais ou publicados. Atualize SRI e manifesto após cada mudança autorizada conforme `SECURITY.md`.

## Publicação

`main` é a fonte de trabalho e `gh-pages` publica o site. Promover alterações com fast-forward depois de validar; não usar force push.
