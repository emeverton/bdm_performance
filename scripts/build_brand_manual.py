#!/usr/bin/env python3
"""Generate the BDM Performance visual identity manual as a polished PDF."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "Manual_Identidade_Visual_BDM_CLevel.pdf"
LOGO = ROOT / "assets" / "ads" / "logo-bdm-original.png"
SYMBOL = ROOT / "assets" / "brand" / "simbolo-bdm.png"
HERO = ROOT / "assets" / "bdm-hero-1920.webp"
FONT_REGULAR = ROOT / "assets" / "ads" / "fonts" / "Montserrat-Regular.ttf"
FONT_BOLD = ROOT / "assets" / "ads" / "fonts" / "Montserrat-Bold.ttf"

W, H = landscape(A4)
GREEN = HexColor("#00AB58")
GREEN_LIGHT = HexColor("#19D978")
INK = HexColor("#090C0B")
GRAPHITE = HexColor("#2D3434")
PAPER = HexColor("#F4F7F5")
MUTED = HexColor("#AAB4AC")
LINE = Color(1, 1, 1, alpha=0.12)
WHITE_08 = Color(1, 1, 1, alpha=0.08)


pdfmetrics.registerFont(TTFont("Montserrat", str(FONT_REGULAR)))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", str(FONT_BOLD)))


def draw_cover_image(c: canvas.Canvas, image_path: Path, x: float, y: float, w: float, h: float, opacity: float = 1) -> None:
    image = ImageReader(str(image_path))
    iw, ih = image.getSize()
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, w, h)
    c.clipPath(clip, stroke=0, fill=0)
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(opacity)
    c.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")
    c.restoreState()


def bg(c: canvas.Canvas, page: int, section: str = "BDM PERFORMANCE") -> None:
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(Color(0, 0.67, 0.35, alpha=0.08))
    c.setLineWidth(0.35)
    step = 42
    for x in range(0, int(W) + step, step):
        c.line(x, 0, x, H)
    for y in range(0, int(H) + step, step):
        c.line(0, y, W, y)
    c.setFillColor(MUTED)
    c.setFont("Montserrat-Bold", 7)
    c.drawString(46, 25, section)
    c.drawRightString(W - 46, 25, f"{page:02d}  ·  SISTEMA VISUAL 1.0  ·  CRIADO POR VELTRUS")
    c.setStrokeColor(Color(1, 1, 1, alpha=0.09))
    c.line(46, 39, W - 46, 39)


def tag(c: canvas.Canvas, text: str, x: float, y: float) -> None:
    c.setStrokeColor(GREEN)
    c.setLineWidth(3)
    c.line(x, y + 5, x + 34, y + 5)
    c.setFillColor(MUTED)
    c.setFont("Montserrat-Bold", 8)
    c.drawString(x + 46, y, text.upper())


def title(c: canvas.Canvas, text: str, x: float, y: float, size: float = 34, max_width: float = 700, leading: float | None = None) -> float:
    leading = leading or size * 1.08
    style = ParagraphStyle("title", fontName="Montserrat-Bold", fontSize=size, leading=leading, textColor=PAPER, alignment=TA_LEFT, spaceAfter=0)
    p = Paragraph(text, style)
    _, ph = p.wrap(max_width, H)
    p.drawOn(c, x, y - ph)
    return y - ph


def body(c: canvas.Canvas, text: str, x: float, y: float, width: float, size: float = 11, color=MUTED, leading: float | None = None) -> float:
    style = ParagraphStyle("body", fontName="Montserrat", fontSize=size, leading=leading or size * 1.5, textColor=color, alignment=TA_LEFT)
    p = Paragraph(text, style)
    _, ph = p.wrap(width, H)
    p.drawOn(c, x, y - ph)
    return y - ph


def pill(c: canvas.Canvas, text: str, x: float, y: float, fill=GREEN, text_color=INK, width: float | None = None) -> float:
    c.setFont("Montserrat-Bold", 8)
    width = width or c.stringWidth(text.upper(), "Montserrat-Bold", 8) + 28
    c.setFillColor(fill)
    c.roundRect(x, y, width, 26, 13, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.drawCentredString(x + width / 2, y + 9, text.upper())
    return width


def card(c: canvas.Canvas, x: float, y: float, w: float, h: float, heading: str, copy: str, number: str | None = None) -> None:
    c.setFillColor(WHITE_08)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 12, fill=1, stroke=1)
    if number:
        c.setFillColor(GREEN)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(x + 18, y + h - 25, number)
        heading_y = y + h - 49
    else:
        heading_y = y + h - 30
    c.setFillColor(PAPER)
    c.setFont("Montserrat-Bold", 12)
    c.drawString(x + 18, heading_y, heading)
    body(c, copy, x + 18, heading_y - 13, w - 36, 8.5, MUTED, 12.5)


def logo_card(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    h = w * 0.31
    c.setFillColor(white)
    c.roundRect(x, y, w, h, 13, fill=1, stroke=0)
    c.drawImage(str(LOGO), x + 16, y + 11, w - 32, h - 22, mask="auto", preserveAspectRatio=True, anchor="c")


def section_start(c: canvas.Canvas, page: int, label: str, heading: str, copy: str | None = None) -> None:
    bg(c, page, label)
    tag(c, label, 52, H - 72)
    title(c, heading, 52, H - 100, 34, 735)
    if copy:
        body(c, copy, 52, H - 190, 690, 10.5, MUTED)


def page_cover(c: canvas.Canvas) -> None:
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_cover_image(c, HERO, W * 0.42, 0, W * 0.58, H)
    c.saveState()
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(0.9)
    c.setFillColor(INK)
    c.rect(0, 0, W * 0.61, H, fill=1, stroke=0)
    c.restoreState()
    c.setStrokeColor(GREEN)
    c.setLineWidth(5)
    c.line(52, H - 96, 112, H - 96)
    logo_card(c, 52, H - 176, 250)
    c.setFillColor(PAPER)
    c.setFont("Montserrat-Bold", 35)
    c.drawString(52, 255, "MANUAL DE")
    c.drawString(52, 210, "IDENTIDADE VISUAL")
    c.setFillColor(GREEN_LIGHT)
    c.drawString(52, 165, "BDM PERFORMANCE")
    c.setFillColor(MUTED)
    c.setFont("Montserrat", 10)
    c.drawString(52, 126, "Sistema operacional de marca · Versão 1.0 · Setembro de 2026")
    c.setFont("Montserrat-Bold", 8)
    c.drawString(52, 42, "CONSOLIDADO E PRODUZIDO POR VELTRUS")
    c.showPage()


def page_foundation(c: canvas.Canvas) -> None:
    section_start(c, 2, "01 · FUNDAÇÃO", "A marca deve parecer engenharia antes de parecer propaganda.", "A BDM ocupa um território técnico: precisão, experiência de oficina e capacidade de entregar retaguarda para quem atende o mercado automotivo.")
    cards = [
        ("PROPÓSITO", "Conectar profissionais e oficinas à engenharia BDM para ampliar a capacidade de atendimento.", "01"),
        ("PROMESSA", "Você atende o mercado. A BDM entra com desenvolvimento e suporte técnico.", "02"),
        ("PERSONALIDADE", "Técnica, segura, direta, experiente e contemporânea. Nunca espalhafatosa.", "03"),
        ("PÚBLICO", "Oficinas, centros automotivos, consultores e representantes com atuação regional.", "04"),
    ]
    for i, item in enumerate(cards):
        card(c, 52 + (i % 2) * 370, 78 + (1 - i // 2) * 145, 342, 122, item[0], item[1], item[2])
    c.showPage()


def page_logo(c: canvas.Canvas) -> None:
    section_start(c, 3, "02 · MARCA", "O símbolo conduz. O nome confirma.", "O conjunto deve ser usado integralmente sempre que houver espaço. O símbolo isolado é reservado a avatares, favicons e aplicações de reconhecimento consolidado.")
    c.setFillColor(white)
    c.roundRect(52, 92, 470, 250, 18, fill=1, stroke=0)
    c.drawImage(str(LOGO), 92, 170, 390, 107, mask="auto", preserveAspectRatio=True)
    c.setFillColor(white)
    c.roundRect(548, 92, 242, 250, 18, fill=1, stroke=1)
    c.drawImage(str(SYMBOL), 594, 164, 150, 136, mask="auto", preserveAspectRatio=True, anchor="c")
    c.setFillColor(INK)
    c.setFont("Montserrat-Bold", 11)
    c.drawString(570, 120, "SÍMBOLO · USO RESTRITO")
    pill(c, "MASTER PREFERENCIAL", 52, 58, GREEN)
    c.showPage()


def page_logo_rules(c: canvas.Canvas) -> None:
    section_start(c, 4, "03 · PROTEÇÃO", "Clareza visual exige respiro e tamanho mínimo.")
    logo_card(c, 68, 258, 330)
    c.setStrokeColor(GREEN)
    c.setLineWidth(1.2)
    c.rect(48, 238, 370, 141, fill=0, stroke=1)
    for x, y, label in [(48, 388, "1X"), (428, 308, "1X"), (48, 218, "1X")]:
        c.setFillColor(GREEN)
        c.setFont("Montserrat-Bold", 8)
        c.drawString(x, y, label)
    card(c, 462, 260, 328, 120, "ÁREA DE PROTEÇÃO", "Mantenha ao redor do logo uma margem mínima equivalente à largura interna do símbolo.", "01")
    card(c, 462, 118, 328, 120, "TAMANHO MÍNIMO", "Digital: 120 px de largura. Impresso: 32 mm. A assinatura PERFORMANCE deve permanecer legível.", "02")
    pill(c, "Nunca comprimir ou redesenhar", 68, 92, GRAPHITE, PAPER, 250)
    c.showPage()


def page_color(c: canvas.Canvas) -> None:
    section_start(c, 5, "04 · COR", "Verde como sinal. Grafite como estrutura.", "A proporção recomendada privilegia superfícies escuras e neutras. O verde aparece em pontos de decisão, energia técnica e leitura de prioridade.")
    swatches = [
        (GREEN, "VERDE BDM", "#00AB58", "Ação, energia e destaque"),
        (GRAPHITE, "GRAFITE", "#2D3434", "Marca, estrutura e apoio"),
        (INK, "PRETO TÉCNICO", "#090C0B", "Fundos e profundidade"),
        (PAPER, "BRANCO MINERAL", "#F4F7F5", "Texto e superfícies claras"),
    ]
    for i, (color, name, value, role) in enumerate(swatches):
        x = 52 + i * 190
        c.setFillColor(color)
        c.roundRect(x, 170, 164, 170, 14, fill=1, stroke=0)
        c.setFillColor(PAPER if color != PAPER else INK)
        c.setFont("Montserrat-Bold", 10)
        c.drawString(x + 14, 205, name)
        c.setFont("Montserrat", 9)
        c.drawString(x + 14, 188, value)
        body(c, role, x, 150, 164, 8.5, MUTED)
    c.setFillColor(MUTED)
    c.setFont("Montserrat-Bold", 8)
    c.drawString(52, 94, "PROPORÇÃO OPERACIONAL")
    c.setFillColor(INK)
    c.roundRect(52, 62, 520, 22, 11, fill=1, stroke=0)
    c.setFillColor(GRAPHITE)
    c.roundRect(52, 62, 330, 22, 11, fill=1, stroke=0)
    c.setFillColor(PAPER)
    c.roundRect(52, 62, 165, 22, 11, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.roundRect(52, 62, 55, 22, 11, fill=1, stroke=0)
    c.showPage()


def page_type(c: canvas.Canvas) -> None:
    section_start(c, 6, "05 · TIPOGRAFIA", "Montserrat cria força sem perder precisão.")
    c.setFillColor(PAPER)
    c.setFont("Montserrat-Bold", 54)
    c.drawString(52, 340, "Aa  ENGINEERING")
    c.setFillColor(GREEN)
    c.setFont("Montserrat-Bold", 16)
    c.drawString(54, 312, "MONTSERRAT BOLD · HEADLINES E CTA")
    c.setFillColor(PAPER)
    c.setFont("Montserrat", 24)
    c.drawString(52, 250, "Precisão técnica em cada aplicação.")
    c.setFillColor(MUTED)
    c.setFont("Montserrat", 10)
    c.drawString(54, 226, "MONTSERRAT REGULAR · TEXTO, LEGENDA E INFORMAÇÃO")
    rules = [
        ("H1", "48–72 px", "Bold · 100% a 108%"),
        ("H2", "32–48 px", "Bold · 105% a 115%"),
        ("BODY", "16–20 px", "Regular · 145% a 165%"),
        ("LABEL", "11–14 px", "Bold · caixa alta · tracking amplo"),
    ]
    for i, (level, scale, spec) in enumerate(rules):
        card(c, 52 + i * 185, 70, 166, 108, level, f"{scale}<br/>{spec}", f"0{i+1}")
    c.showPage()


def page_layout(c: canvas.Canvas) -> None:
    section_start(c, 7, "06 · LAYOUT", "Hierarquia forte. Espaço controlado. Conversão visível.")
    x, y, w, h = 52, 84, 480, 300
    c.setFillColor(WHITE_08)
    c.roundRect(x, y, w, h, 14, fill=1, stroke=1)
    c.setStrokeColor(Color(0, .67, .35, alpha=.25))
    for i in range(1, 12):
        gx = x + i * w / 12
        c.line(gx, y, gx, y + h)
    c.setFillColor(PAPER)
    c.setFont("Montserrat-Bold", 25)
    c.drawString(x + 26, y + h - 65, "UMA IDEIA")
    c.drawString(x + 26, y + h - 98, "POR PEÇA.")
    c.setFillColor(GREEN)
    c.roundRect(x + 26, y + 42, 175, 38, 19, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Montserrat-Bold", 8)
    c.drawCentredString(x + 113, y + 56, "CTA OBJETIVO")
    card(c, 560, 262, 230, 122, "GRID", "12 colunas no desktop. Quatro colunas no mobile. Alinhamento sempre aparente.", "01")
    card(c, 560, 120, 230, 122, "ESPAÇAMENTO", "Base de 8 px. Seções amplas. Elementos críticos nunca competem entre si.", "02")
    c.showPage()


def page_photo(c: canvas.Canvas) -> None:
    section_start(c, 8, "07 · FOTOGRAFIA", "O visual deve provar proximidade com engenharia e oficina.")
    images = [
        ROOT / "assets" / "ads" / "final" / "bdm-engenharia-paisagem.png",
        ROOT / "assets" / "ads" / "final" / "bdm-oficina-paisagem.png",
        ROOT / "assets" / "ads" / "final" / "bdm-rede-paisagem.png",
    ]
    for i, image in enumerate(images):
        x = 52 + i * 250
        draw_cover_image(c, image, x, 208, 226, 118)
        c.setFillColor(PAPER)
        c.setFont("Montserrat-Bold", 9)
        c.drawString(x, 190, ["MACRO TÉCNICO", "OPERAÇÃO REAL", "REDE E ESCALA"][i])
    cards = [
        ("FAZER", "Metal realista, oficina organizada, luz controlada, máquinas e interfaces plausíveis."),
        ("EVITAR", "Carros em corrida, fogo, fumaça excessiva, pose agressiva ou tecnologia genérica."),
        ("COMPOSIÇÃO", "Assunto técnico de um lado e área negativa do outro para copy e CTA."),
    ]
    for i, item in enumerate(cards):
        card(c, 52 + i * 250, 62, 226, 106, item[0], item[1], f"0{i+1}")
    c.showPage()


def page_3d(c: canvas.Canvas) -> None:
    section_start(c, 9, "08 · ASSINATURA 3D", "A tecnologia deve parecer integrada ao mundo real.")
    draw_cover_image(c, ROOT / "assets" / "ads" / "final" / "bdm-engenharia-feed.png", 52, 72, 280, 350)
    items = [
        ("ENERGIA VERDE", "Use o verde como fluxo de dados, contorno técnico e ponto de energia. Nunca como neon decorativo."),
        ("MATERIAIS", "Alumínio usinado, carbono, vidro fumê, polímero fosco e superfícies de oficina."),
        ("PROFUNDIDADE", "Foreground, assunto principal e ambiente devem formar três planos claramente legíveis."),
        ("REALISMO", "Componentes e conexões precisam permanecer mecanicamente plausíveis."),
    ]
    for i, item in enumerate(items):
        card(c, 365 + (i % 2) * 215, 252 - (i // 2) * 150, 196, 130, item[0], item[1], f"0{i+1}")
    c.showPage()


def page_campaign(c: canvas.Canvas) -> None:
    section_start(c, 10, "09 · SISTEMA DE CAMPANHA", "Três territórios para uma mesma proposta de valor.")
    concepts = [
        ("01", "AUTORIDADE", "Remap com engenharia na retaguarda.", "Quero avaliar a parceria"),
        ("02", "OPERAÇÃO", "Uma nova frente de serviço para sua oficina.", "Conhecer o modelo"),
        ("03", "EXPANSÃO", "Sua região pode ser o próximo Ponto de Apoio BDM.", "Consultar minha região"),
    ]
    for i, item in enumerate(concepts):
        x = 52 + i * 250
        c.setFillColor(WHITE_08)
        c.roundRect(x, 105, 225, 280, 14, fill=1, stroke=1)
        c.setFillColor(GREEN)
        c.setFont("Montserrat-Bold", 28)
        c.drawString(x + 18, 340, item[0])
        c.setFillColor(MUTED)
        c.setFont("Montserrat-Bold", 8)
        c.drawString(x + 18, 314, item[1])
        body(c, f"<b>{item[2]}</b>", x + 18, 285, 188, 14, PAPER, 18)
        pill(c, item[3], x + 18, 130, GREEN, INK, 188)
    c.showPage()


def page_feed(c: canvas.Canvas) -> None:
    section_start(c, 11, "10 · FEED 4:5", "Feed prioriza leitura rápida e presença de marca.")
    draw_cover_image(c, ROOT / "assets" / "ads" / "final" / "bdm-oficina-feed.png", 52, 66, 285, 356)
    card(c, 370, 300, 420, 122, "SAFE AREA", "Mantenha logo, headline e CTA a pelo menos 7% das bordas. O assunto pode sangrar, a mensagem não.", "01")
    card(c, 370, 158, 420, 122, "ORDEM DE LEITURA", "Marca → território → headline → argumento → CTA. Não inserir um segundo benefício concorrente.", "02")
    card(c, 370, 66, 420, 72, "EXPORT", "1080 × 1350 px · PNG · RGB · sem compressão destrutiva", "03")
    c.showPage()


def page_formats(c: canvas.Canvas) -> None:
    section_start(c, 12, "11 · STORY E PAISAGEM", "O conceito deve ser recomposto para cada proporção.")
    draw_cover_image(c, ROOT / "assets" / "ads" / "final" / "bdm-rede-story.png", 52, 70, 190, 320)
    draw_cover_image(c, ROOT / "assets" / "ads" / "final" / "bdm-rede-paisagem.png", 278, 208, 480, 220)
    card(c, 278, 70, 230, 126, "STORY 9:16", "1080 × 1920 px. Preservar topo e rodapé contra sobreposições da plataforma.", "01")
    card(c, 528, 70, 230, 126, "PAISAGEM", "1200 × 628 px. Copy curta e assunto deslocado para permitir leitura lateral.", "02")
    c.showPage()


def page_copy(c: canvas.Canvas) -> None:
    section_start(c, 13, "12 · VOZ E CTA", "Direto, técnico e consultivo. Nunca absoluto.")
    columns = [
        ("USAR", ["Engenharia na retaguarda", "Avalie o modelo", "Consulte sua região", "Desenvolvimento próprio", "Ponto de Apoio BDM"]),
        ("EVITAR", ["Potência garantida", "Zero retrabalho", "Lucro imediato", "Exclusividade total", "Suporte 24/7 sem validação"]),
    ]
    for i, (heading, rows) in enumerate(columns):
        x = 52 + i * 375
        c.setFillColor(GREEN if i == 0 else GRAPHITE)
        c.roundRect(x, 350, 340, 42, 10, fill=1, stroke=0)
        c.setFillColor(INK if i == 0 else PAPER)
        c.setFont("Montserrat-Bold", 11)
        c.drawString(x + 18, 365, heading)
        for j, row in enumerate(rows):
            yy = 313 - j * 46
            c.setFillColor(Color(1, 1, 1, alpha=.055))
            c.roundRect(x, yy, 340, 34, 7, fill=1, stroke=0)
            c.setFillColor(GREEN if i == 0 else MUTED)
            c.setFont("Montserrat-Bold", 8)
            c.drawString(x + 15, yy + 12, "✓" if i == 0 else "×")
            c.setFillColor(PAPER)
            c.setFont("Montserrat", 9)
            c.drawString(x + 36, yy + 11, row)
    pill(c, "CTA deve descrever a próxima decisão", 52, 62, GREEN, INK, 270)
    c.showPage()


def page_digital(c: canvas.Canvas) -> None:
    section_start(c, 14, "13 · DIGITAL E ACESSIBILIDADE", "Performance visual também é performance técnica.")
    checks = [
        ("CONTRASTE", "Texto normal precisa atender WCAG AA. Verde não substitui branco em textos longos."),
        ("MOVIMENTO", "Efeitos devem respeitar prefers-reduced-motion e nunca impedir leitura ou ação."),
        ("IMAGEM", "Use versões responsivas, WebP para interface e PNG para arquivo final de mídia."),
        ("CTA", "Um verbo, uma intenção e contraste inequívoco. Área mínima confortável para toque."),
        ("SEO", "Imagens públicas devem ter alt text descritivo. Páginas de revisão permanecem noindex."),
        ("DADOS", "Rastreamento deve usar consentimento e identificadores autorizados. Nunca inventar IDs."),
    ]
    for i, item in enumerate(checks):
        card(c, 52 + (i % 3) * 250, 260 - (i // 3) * 150, 225, 126, item[0], item[1], f"0{i+1}")
    c.showPage()


def page_misuse(c: canvas.Canvas) -> None:
    section_start(c, 15, "14 · USOS PROIBIDOS", "Consistência é uma regra operacional, não uma preferência.")
    mistakes = [
        "Não alterar proporção, inclinação ou espaçamento do logo.",
        "Não usar vermelho como cor proprietária da BDM.",
        "Não aplicar glow excessivo, cromado artificial ou estética gamer.",
        "Não colocar texto sobre áreas de alta complexidade visual.",
        "Não misturar públicos B2C e B2B na mesma peça.",
        "Não publicar números de potência, economia, ROI ou payback sem aprovação.",
        "Não usar fotografia genérica que pareça banco de imagens corporativo.",
        "Não transformar CTA em slogan. CTA indica a próxima ação.",
    ]
    for i, mistake in enumerate(mistakes):
        x = 52 + (i % 2) * 370
        y = 350 - (i // 2) * 70
        c.setFillColor(Color(1, 1, 1, alpha=.055))
        c.roundRect(x, y, 342, 52, 10, fill=1, stroke=1)
        c.setFillColor(GREEN)
        c.setFont("Montserrat-Bold", 12)
        c.drawString(x + 16, y + 20, "×")
        body(c, mistake, x + 42, y + 35, 280, 8.5, PAPER, 11)
    c.showPage()


def page_governance(c: canvas.Canvas) -> None:
    section_start(c, 16, "15 · GOVERNANÇA", "Double-check antes de qualquer publicação.", "Esta versão consolida o sistema operacional de identidade aplicado à landing page e às campanhas do modelo Ponto de Apoio.")
    checklist = [
        "Logo oficial, proporção e área de proteção preservados",
        "Verde #00AB58 usado como sinal e não como ruído",
        "Montserrat aplicada com hierarquia e legibilidade",
        "Uma promessa principal por peça",
        "Claim comercial validado em fonte atual",
        "CTA descreve uma próxima ação real",
        "Formato, safe area e export conferidos",
        "Contraste, mobile e acessibilidade revisados",
        "Arquivo final comparado ao master aprovado",
        "Owner e data de aprovação registrados",
    ]
    for i, item in enumerate(checklist):
        x = 52 + (i % 2) * 370
        y = 338 - (i // 2) * 52
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.5)
        c.roundRect(x, y, 22, 22, 5, fill=0, stroke=1)
        c.setFillColor(PAPER)
        c.setFont("Montserrat", 9)
        c.drawString(x + 36, y + 7, item)
    c.setFillColor(MUTED)
    c.setFont("Montserrat", 7.5)
    c.drawString(52, 58, "FONTES PRIMÁRIAS: logo colorido original · Arquitetura da marca BDM · análise de design V4 · anotações de reunião · manual de copy.")
    c.showPage()


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
    c.setTitle("Manual de Identidade Visual BDM Performance · C-Level")
    c.setAuthor("Veltrus")
    c.setSubject("Sistema visual operacional da BDM Performance")
    page_cover(c)
    page_foundation(c)
    page_logo(c)
    page_logo_rules(c)
    page_color(c)
    page_type(c)
    page_layout(c)
    page_photo(c)
    page_3d(c)
    page_campaign(c)
    page_feed(c)
    page_formats(c)
    page_copy(c)
    page_digital(c)
    page_misuse(c)
    page_governance(c)
    c.save()
    print(f"PASS: brand manual generated at {OUT}")


if __name__ == "__main__":
    main()
