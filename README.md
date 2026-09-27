# BDM Performance · V4 / Veltrus

Site estático de revisão. Código e assets deste projeto pertencem exclusivamente à BDM Performance.

## Escopo desta versão

- Landing page responsiva com o KV selecionado nesta conversa.
- Rotas estáticas `brand/`, `ads/` e `review/`.
- HTML, CSS e JavaScript sem dependências de runtime.
- `noindex,nofollow` em todas as páginas de revisão.
- Formulário demonstrativo, sem backend, sem envio de dados pessoais e sem conversões reais.

As páginas de marca e anúncios são bases de revisão, não entregáveis aprovados. A imagem da hero é conceitual, gerada por IA, e não comprova instalações, resultados ou veículos de clientes reais.

## Execução local

```sh
python3 -m http.server 8080
```

Abra `http://localhost:8080/`.

## Publicação

O workflow `.github/workflows/pages.yml` valida os arquivos e prepara o deploy para GitHub Pages. A ativação inicial de Pages em Settings → Pages → Source: GitHub Actions exige acesso administrativo específico à configuração de Pages. Um commit enviado não comprova que o site está publicado.

## Gate comercial

Antes de tráfego pago: aprovar peças e copy; definir contato e política de privacidade; conectar e validar endpoint de leads; disparar conversão apenas após confirmação de sucesso do backend; validar a página em dispositivos reais.

Nenhum segredo, token, exportação do CRM ou documento interno do Drive deve ser adicionado a este repositório público.
