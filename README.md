# BDM Performance — site

Site estático, responsivo e sem dependências de runtime. A homepage foi reconstruída a partir do pacote original da BDM Performance e está publicada no GitHub Pages.

## Fontes de conteúdo e identidade

- Logo colorido original: `3. Conteúdos Cliente/logo bdm alta def.png`.
- Arquitetura da marca: `3. Conteúdos Cliente/Arquitetura da marca-BDM-aumentada.pdf` e `.eps`.
- Manual de copy, análise de design e anotações de reunião em `4. Conteúdos V4/Relatórios Social Media`.
- Criativos originais do cliente, usados no acervo da página e convertidos para WebP sem redesenho.

O verde `#00AB58` e o grafite `#2D3434` foram amostrados do logo. A direção usa os neutros recomendados nos arquivos de análise. A página foca em oficinas e parceiros e inclui entusiastas automotivos como público, conforme as notas de reunião.

## Página e contato

- Homepage com foco no modelo de Ponto de Apoio, retaguarda técnica e aplicações BDM.
- CTAs abrem uma mensagem pré-preenchida no WhatsApp oficial informado no site da BDM: `+55 44 98801-8242` (`https://www.bdmperformance.com.br/`).
- O site não recebe nem armazena dados de contato; não há formulário, CRM ou pixel de conversão.
- Claims absolutos de potência, economia, exclusividade de software e retrabalho zero foram evitados.
- A homepage é indexável. As rotas auxiliares `brand/`, `ads/` e `review/` permanecem com `noindex,nofollow`.

## Validação

```sh
node --check app.js
python3 scripts/validate.py
```

## Publicação

`main` é a fonte de trabalho. `gh-pages` publica o site. Promover alterações com fast-forward após validação; não usar force push.
