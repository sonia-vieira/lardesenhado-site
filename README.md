# Lar Desenhado · o site e o blog

O site público do Lar Desenhado, em `lardesenhado.com.br`, publicado pelo GitHub Pages a partir da pasta `docs/`.
Quem cuida: a sessão VENDAS. O app fica em outro repositório (`lar-desenhado`).

- `fonte/posts/` — os artigos, um `.md` por artigo (o cabeçalho está explicado no `gerar.py`).
- `fonte/estatico/` — o estilo, o símbolo, os ícones e as imagens.
- `gerar.py` — gera o site em `docs/`. Rodar `python gerar.py` antes de cada envio.

Enquanto o conteúdo não estiver aprovado, o site sai com `noindex` (o Google não indexa): `INDEXAR = False` no
`gerar.py`.
