"""Lar Desenhado — gera o site e o blog (v11, 13/10/2026, sessão VENDAS: as duas trilhas, logo depois o quarto do bebê; o caderno real).

Lê `fonte/posts/*.md` e escreve o site pronto em `docs/`, que o GitHub Pages publica.
Rodar: python gerar.py

Cada artigo é um .md com o cabeçalho:
---
titulo: O título
data: 2026-10-20
descricao: Uma frase para o Google e para a lista do blog.
imagem: img/arquivo.webp
legenda_imagem: O que a imagem mostra.
rascunho: sim        (sim = não publica)
---
"""
import html
import pathlib
import re
import shutil

RAIZ = pathlib.Path(__file__).parent
FONTE = RAIZ / "fonte"
SAIDA = RAIZ / "docs"

DOMINIO = "https://lardesenhado.com.br"
APP = "https://lardesenhado.lovable.app"
INSTAGRAM = "https://www.instagram.com/lardesenhado/"
# Enquanto ela não aprovar o conteúdo, o Google não indexa (noindex).
INDEXAR = False

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def data_por_extenso(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


# ---------- markdown simples (o que os artigos usam) ----------
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[(.+?)\]\((\S+?)\)", r'<a href="\2">\1</a>', t)
    return t


def markdown(texto, prefixo):
    linhas = texto.strip().splitlines()
    out, para, lista = [], [], None

    def fecha_para():
        if para:
            txt = inline(' '.join(para))
            if txt.startswith("<strong>No Lar Desenhado,</strong>"):
                out.append(f'<aside class="chamada"><p>{txt}</p>'
                           f'<a class="botao-leve" href="{prefixo}conheca/">Conhecer o Lar Desenhado</a></aside>')
            else:
                out.append(f"<p>{txt}</p>")
            para.clear()

    def fecha_lista():
        nonlocal lista
        if lista:
            tag, itens = lista
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in itens) + f"</{tag}>")
            lista = None

    for ln in linhas:
        s = ln.strip()
        img = re.match(r'!\[(.*?)\]\((\S+?)(?:\s+"(.*?)")?\)$', s)
        if not s:
            fecha_para(); fecha_lista()
        elif s.startswith("### "):
            fecha_para(); fecha_lista(); out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "):
            fecha_para(); fecha_lista(); out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("> "):
            fecha_para(); fecha_lista(); out.append(f"<blockquote><p>{inline(s[2:])}</p></blockquote>")
        elif img:
            fecha_para(); fecha_lista()
            alt, src, leg = img.group(1), img.group(2), img.group(3)
            src = src if src.startswith("http") else prefixo + src
            cap = f"<figcaption>{inline(leg)}</figcaption>" if leg else ""
            out.append(f'<figure><img src="{src}" alt="{html.escape(alt)}" loading="lazy">{cap}</figure>')
        elif re.match(r"^[-*] ", s):
            fecha_para()
            if not lista or lista[0] != "ul":
                fecha_lista(); lista = ("ul", [])
            lista[1].append(s[2:])
        elif re.match(r"^\d+\. ", s):
            fecha_para()
            if not lista or lista[0] != "ol":
                fecha_lista(); lista = ("ol", [])
            lista[1].append(re.sub(r"^\d+\. ", "", s))
        else:
            fecha_lista(); para.append(s)
    fecha_para(); fecha_lista()
    return "\n".join(out)


def ler_post(arq):
    texto = arq.read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", texto, re.S)
    meta = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["corpo"] = m.group(2)
    meta["slug"] = arq.stem
    return meta


# ---------- moldura comum ----------
def pagina(titulo, descricao, corpo, prefixo, caminho, imagem=None):
    robots = "index,follow" if INDEXAR else "noindex,nofollow"
    og_img = f'<meta property="og:image" content="{DOMINIO}/{imagem}">' if imagem else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo)}</title>
<meta name="description" content="{html.escape(descricao)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{DOMINIO}/{caminho}">
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{html.escape(descricao)}">
<meta property="og:locale" content="pt_BR">
{og_img}
<link rel="icon" href="{prefixo}favicon.ico">
<link rel="apple-touch-icon" href="{prefixo}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefixo}estilo.css">
</head>
<body>
<header class="topo"><div class="envolve">
  <a class="marca" href="{prefixo}"><img src="{prefixo}simbolo.svg" alt=""><span>Lar Desenhado<small>projetos para quartos de bebê e infantis</small></span></a>
  <nav class="menu"><a href="{prefixo}blog/">Artigos</a><a href="{INSTAGRAM}">Instagram</a><a class="discreto" href="{prefixo}conheca/">Conheça o app</a></nav>
</div></header>
{corpo}
<footer class="rodape"><div class="envolve">
  <span>Lar Desenhado · projetos para quartos de bebê e infantis · <a href="{prefixo}conheca/">Conheça o app</a></span>
  <span><a href="{INSTAGRAM}">@lardesenhado</a></span>
</div></footer>
</body>
</html>
"""


EDITORIAS = ["Medida que protege", "Cada idade, um quarto", "Quarto pequeno", "Cor, luz e tecido",
             "Antes de comprar", "Mão na massa"]


def cartao(x, prefixo, grande=False):
    img = ""
    if x.get("imagem"):
        img = f'<img src="{prefixo}{x["imagem"]}" alt="{html.escape(x.get("legenda_imagem", ""))}" loading="lazy">'
    classe = "cartao grande" if grande else "cartao"
    return (f'<article class="{classe}"><a class="foto" href="{prefixo}blog/{x["slug"]}/">{img}</a><div>'
            f'<p class="editoria">{html.escape(x.get("editoria", ""))}</p>'
            f'<h2><a href="{prefixo}blog/{x["slug"]}/">{html.escape(x["titulo"])}</a></h2>'
            f'<p>{html.escape(x["descricao"])}</p></div></article>')


def inicio(posts):
    p = ""
    if posts:
        destaque = cartao(posts[0], p, grande=True)
        outros = "".join(cartao(x, p) for x in posts[1:7])
    else:
        destaque, outros = '<p class="vazio">Os primeiros artigos chegam em breve.</p>', ""
    com = {x.get("editoria") for x in posts}
    editorias = "".join(
        f'<li class="{"tem" if e in com else "breve"}">{html.escape(e)}</li>' for e in EDITORIAS)
    corpo = f"""
<section class="cabeca-revista"><div class="envolve">
  <p class="assinatura">artigos do Lar Desenhado</p>
  <h1>Ideias e medidas para o quarto do seu filho</h1>
  <p class="apoio">Segurança, cada idade, quarto pequeno, cor e o que conferir antes de comprar. Com calma e com fonte.</p>
</div></section>
<section class="envolve">{destaque}</section>
<section class="envolve"><div class="grade">{outros}</div></section>
<section class="faixa"><div class="envolve">
  <h2>As seções</h2>
  <ul class="editorias">{editorias}</ul>
</div></section>
"""
    return pagina("Lar Desenhado · ideias e medidas para o quarto do seu filho",
                  "Ideias e medidas para o quarto de bebê e o quarto infantil: segurança, cada idade, quarto pequeno e cor.",
                  corpo, p, "", posts[0]["imagem"] if posts else None)


def conheca():
    p = "../"
    perguntas = [
        ("Preciso saber desenhar ou entender de projeto?",
         "Não. O desenho da criança é do jeito dela, e a sua planta pode ser um rascunho no papel. "
         "As medidas, a organização e o projeto ficam com a gente, passo a passo."),
        ("Meu filho ainda é bebê. Como ele participa?",
         "No quarto de bebê, quem desenha é você, junto com o irmão mais velho, se houver. O quarto já nasce "
         "pensando na próxima fase."),
        ("Para que idade serve?",
         "Do bebê aos 12 anos. O episódio, as perguntas e as escolhas mudam com a fase: 0 a 3, 3 a 6, 6 a 9 e 9 a 12."),
        ("Preciso de TV?",
         "Não. O episódio passa na TV, no computador ou no celular. A TV só deixa o momento mais gostoso, "
         "com todo mundo na sala."),
        ("E se forem dois irmãos no mesmo quarto?",
         "Os dois desenham, os dois participam e cada um ganha o seu certificado de mini designer."),
        ("Posso aproveitar os móveis que já tenho?",
         "Pode. Você conta o que já tem em casa e quer manter, e isso entra no projeto."),
        ("Móveis prontos ou sob medida?",
         "Os dois, ou uma mistura. Para o sob medida, saem os desenhos para levar ao marceneiro."),
        ("Preciso comprar nas lojas indicadas?",
         "Não. A lista do que comprar mostra onde encontrar cada item, e você compra onde quiser. "
         "Alguns links nos dão uma comissão, sem nenhum custo a mais para você."),
        ("É seguro?",
         "As alturas, as passagens e as proteções seguem as normas e os guias de quarto infantil, "
         "sempre com a fonte. Segurança vem antes da decoração."),
    ]
    faq = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(r)}</p></details>"
                  for q, r in perguntas)
    folhas = [("folha-1", "A planta do quarto, com as medidas"),
              ("folha-2", "A vista de cada parede"),
              ("folha-3", "Como vai ficar, em imagem"),
              ("folha-4", "A lista do que comprar")]
    figs = "".join(f'<figure><img src="{p}img/{a}.webp" alt="{html.escape(b)}" loading="lazy"><figcaption>{html.escape(b)}</figcaption></figure>'
                   for a, b in folhas)
    corpo = f"""
<section class="abertura"><div class="envolve">
  <div>
    <p class="assinatura">projetos para quartos de bebê e infantis</p>
    <h1>O quarto do seu filho, criado em família.</h1>
    <p class="apoio">Uma experiência guiada em que pais e filhos imaginam, desenham e projetam juntos o quarto de
    cada fase, do bebê aos 12 anos. Do primeiro rabisco ao projeto pronto para fazer.</p>
    <a class="botao" href="{APP}">Começar nosso espaço</a>
    <p class="nota">No seu tempo, com a família reunida.</p>
  </div>
  <figure><img src="{p}img/familia-desenhando.webp" alt="Uma família no chão da sala: a filha pequena e o filho mais velho desenham, e o pai rabisca a planta numa folha comum" width="928" height="1152"></figure>
</div></section>

<section class="faixa areia"><div class="envolve estreito">
  <h2>Quem melhor sabe o que a sua família sonha é ela mesma</h2>
  <p>O quarto de uma criança guarda muita coisa: o jeito dela, a fase que ela vive, a rotina da casa e o que a família
  quer que ela sinta ali. Por isso, aqui é a família que conduz. A gente guia cada passo, cuida das medidas e da
  segurança, e você decide com calma, sem pressa e sem precisar entender de projeto.</p>
  <p>E a criança não fica de fora: ela participa desde o primeiro desenho.</p>
</div></section>

<section class="faixa"><div class="envolve">
  <h2>Dois caminhos, o mesmo projeto completo</h2>
  <p class="estreito">Você escolhe como quer fazer, e pode trocar no meio do caminho.</p>
  <div class="trilhas">
    <div class="trilha pratica"><p class="rotulo">a trilha prática</p><b>Rápido, do seu jeito</b>Para quem quer resolver
    sem rodeios: poucas perguntas, direto ao ponto, tudo pelo celular. Você conta o essencial, mede, monta e recebe o
    projeto.</div>
    <div class="trilha ludica"><p class="rotulo">a trilha em família</p><b>Uma experiência para viver junto</b>Para quem
    quer fazer do quarto um momento da família: o episódio na sala, o desenho da criança, a sua planta à mão e, no
    fim, o certificado de mini designer.</div>
  </div>
</div></section>

<section class="faixa areia"><div class="envolve bebe">
  <figure><img src="{p}img/quarto-bebe-familia.webp" alt="Um casal à espera do bebê, no quarto que estão preparando, olhando juntos o app no celular" loading="lazy"></figure>
  <div>
    <p class="assinatura">para quem está chegando</p>
    <h2>E o quarto do bebê também</h2>
    <p>Na trilha prática, você faz tudo direto pelo celular, no seu ritmo: conte o que você imagina, meça o quarto, monte e
    veja o quarto do bebê pronto, antes de comprar. E, se houver um irmão mais velho, ele pode desenhar o quarto do
    irmãozinho e já começa a se sentir parte da chegada.</p>
    <p>O quarto nasce pensando nos próximos anos: o berço, a cômoda com trocador, a poltrona das madrugadas e a luz
    baixa para a hora de mamar. E a marcenaria já fica pronta para quando o berço sair e a cama chegar.</p>
    <a class="botao" href="{APP}">Começar o quarto do bebê</a>
  </div>
</div></section>

<section class="faixa"><div class="envolve">
  <h2>As etapas</h2>
  <ol class="jornada">
    <li><b>Sonhar</b>Na trilha em família, começa na sala: todos assistem a um episódio ilustrado, na linguagem da
    idade da criança, que termina com um convite. A criança desenha o quarto que imagina, e você desenha, numa folha comum, a planta do
    quarto como ele é hoje. Depois, uma conversa do jeito do WhatsApp, por texto ou por áudio: o que a família ama, o
    que não pode faltar, o que incomoda hoje. Na trilha prática, são só as perguntas essenciais.</li>
    <li><b>Medir</b>Com a sua planta em mãos, o app guia as medidas, parede por parede, com a altura do teto, as
    portas e as janelas.</li>
    <li><b>Montar</b>A família escolhe junta os móveis, as cores, as frentes e os puxadores, e veem cada peça no lugar,
    em 3D, no tamanho do quarto.</li>
    <li><b>Visualizar</b>As imagens do quarto pronto, antes de comprar qualquer coisa, e o projeto para fazer: a
    planta, as vistas, os desenhos para o marceneiro e a lista do que comprar. A apresentação final começa pelo
    desenho da criança.</li>
  </ol>
</div></section>

<section class="faixa areia"><div class="envolve">
  <h2>No fim, cada um recebe o seu</h2>
  <div class="cada-um">
    <div><b>O mini designer recebe o certificado</b>Cada criança que participou ganha o seu certificado de mini
    designer, no mesmo formato do caderno do projeto: o nome dela e o desenho que ela fez no primeiro dia. Para
    imprimir, pendurar e lembrar que ela ajudou a criar o próprio quarto.</div>
    <div><b>Os pais recebem o projeto completo</b>O caderno do projeto: a luz, as tomadas, as paredes, o chão, o teto,
    a janela, a marcenaria, os móveis, o quarto seguro, o que executar, a ordem da obra e a lista de compras. E as
    imagens do quarto pronto, para fazer com segurança.</div>
  </div>
  <figure class="certificado"><img src="{p}img/certificado-mini-designer.webp" alt="Exemplo do certificado de mini designer: o nome da criança e o desenho que ela fez do quarto" loading="lazy">
  <figcaption>O certificado de mini designer. Exemplo ilustrativo.</figcaption></figure>
</div></section>

<section class="faixa"><div class="envolve">
  <h2>O projeto completo, folha por folha</h2>
  <p class="estreito">Um caderno com tudo o que a obra e as compras precisam, uma coisa por folha, para levar ao
  marceneiro, ao eletricista e à loja. O caderno do exemplo abaixo tem 34 folhas.</p>
  <ul class="editorias partes"><li>Luz</li><li>Tomadas e interruptores</li><li>Paredes</li><li>Chão</li><li>Teto</li><li>Janela</li><li>Marcenaria</li><li>Móveis e decoração</li><li>Clima</li><li>Porta</li><li>O quarto seguro</li><li>O que executar</li><li>A ordem da obra</li><li>A lista de compras</li></ul>
  <div class="folhas caderno"><figure><img src="{p}img/caderno-capa.webp" alt="A capa, com o que tem no caderno" loading="lazy"><figcaption>A capa, com o que tem no caderno</figcaption></figure><figure><img src="{p}img/caderno-luz.webp" alt="A luz do quarto, na planta" loading="lazy"><figcaption>A luz do quarto, na planta</figcaption></figure><figure><img src="{p}img/caderno-parede.webp" alt="Cada parede, com os acabamentos e os m²" loading="lazy"><figcaption>Cada parede, com os acabamentos e os m²</figcaption></figure><figure><img src="{p}img/caderno-marcenaria.webp" alt="A marcenaria, com as medidas" loading="lazy"><figcaption>A marcenaria, com as medidas</figcaption></figure><figure><img src="{p}img/caderno-seguro.webp" alt="O quarto seguro, regra por regra" loading="lazy"><figcaption>O quarto seguro, regra por regra</figcaption></figure><figure><img src="{p}img/caderno-obra.webp" alt="A ordem da obra, passo a passo" loading="lazy"><figcaption>A ordem da obra, passo a passo</figcaption></figure><figure><img src="{p}img/caderno-compras.webp" alt="A lista de compras" loading="lazy"><figcaption>A lista de compras</figcaption></figure></div>
  <p class="nota">Folhas reais do caderno gerado pelo app, num quarto de teste. E, além do caderno: as imagens do
  quarto pronto, vista de cima e parede por parede, e o quarto em 3D para girar e conferir.</p>
</div></section>

<section class="faixa"><div class="envolve">
  <h2>Por que é diferente</h2>
  <div class="cartoes4">
    <div><b>Do seu jeito</b>Rápido e sozinho, ou em família, com a criança desenhando. As escolhas são suas; a
    gente guia, não decide por você.</div>
    <div><b>Medida com fonte</b>As alturas, as passagens e as proteções seguem as normas e os guias de quarto
    infantil. Segurança vem antes da decoração.</div>
    <div><b>O quarto que cresce</b>Cada escolha pensa na idade de agora e na próxima fase, para você não refazer
    tudo daqui a pouco.</div>
    <div><b>No seu tempo</b>Sem reunião marcada. Você para e continua quando puder.</div>
  </div>
</div></section>

<section class="faixa"><div class="envolve estreito">
  <h2>Perguntas frequentes</h2>
  <div class="faq">{faq}</div>
</div></section>

<section class="faixa areia"><div class="envolve fecho">
  <p class="frase">Os seus desejos, as suas escolhas. A gente transforma em espaço.</p>
  <a class="botao" href="{APP}">Vamos preparar esse espaço juntos?</a>
  <p class="nota"><a href="{p}blog/">Ou leia antes os nossos artigos sobre o quarto infantil</a></p>
</div></section>
"""
    return pagina("Conheça o Lar Desenhado · o quarto do seu filho, criado em família",
                  "Pais e filhos imaginam, desenham e projetam juntos o quarto de cada fase, do bebê aos 12 anos. "
                  "No fim, a criança ganha o certificado de mini designer.",
                  corpo, p, "conheca/", "img/familia-desenhando.webp")


def indice_blog(posts):
    p = "../"
    itens = "".join(cartao(x, p) for x in posts) if posts else \
        '<p class="vazio">Os primeiros artigos chegam em breve.</p>'
    corpo = f"""<section class="cabeca-revista"><div class="envolve"><h1>Todos os artigos</h1></div></section>
<section class="envolve"><div class="grade">{itens}</div></section>"""
    return pagina("Artigos · Lar Desenhado", "Ideias e medidas para o quarto de bebê e o quarto infantil.",
                  corpo, p, "blog/")


def artigo(x):
    p = "../../"
    fig = ""
    if x.get("imagem"):
        leg = f'<figcaption>{inline(x.get("legenda_imagem", ""))}</figcaption>' if x.get("legenda_imagem") else ""
        fig = f'<figure><img src="{p}{x["imagem"]}" alt="{html.escape(x.get("legenda_imagem", ""))}">{leg}</figure>'
    corpo = f"""<main class="artigo">
<p class="editoria">{html.escape(x.get("editoria", ""))}</p>
<h1>{html.escape(x["titulo"])}</h1>
<p class="data">{html.escape(x.get("autoria", "Equipe Lar Desenhado"))} · {data_por_extenso(x["data"])}</p>
{fig}
{markdown(x["corpo"], p)}
</main>"""
    return pagina(f'{x["titulo"]} · Lar Desenhado', x["descricao"], corpo, p, f'blog/{x["slug"]}/',
                  x.get("imagem"))


def escreve(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def main():
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    shutil.copytree(FONTE / "estatico", SAIDA)
    (SAIDA / ".nojekyll").write_text("", encoding="utf-8")
    if (FONTE / "CNAME").exists():
        shutil.copy(FONTE / "CNAME", SAIDA / "CNAME")

    posts = [ler_post(a) for a in sorted((FONTE / "posts").glob("*.md"))]
    posts = [x for x in posts if x.get("rascunho", "nao").lower() not in ("sim", "s", "yes")]
    posts.sort(key=lambda x: x["data"], reverse=True)

    escreve(SAIDA / "index.html", inicio(posts))
    escreve(SAIDA / "blog" / "index.html", indice_blog(posts))
    escreve(SAIDA / "conheca" / "index.html", conheca())
    for x in posts:
        escreve(SAIDA / "blog" / x["slug"] / "index.html", artigo(x))

    if INDEXAR:
        urls = ["", "blog/", "conheca/"] + [f'blog/{x["slug"]}/' for x in posts]
        escreve(SAIDA / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + "".join(f"<url><loc>{DOMINIO}/{u}</loc></url>" for u in urls) + "</urlset>\n")
        escreve(SAIDA / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n")
    else:
        escreve(SAIDA / "robots.txt", "User-agent: *\nDisallow: /\n")
    print(f"ok: {len(posts)} artigo(s) publicados em {SAIDA}")


if __name__ == "__main__":
    main()
