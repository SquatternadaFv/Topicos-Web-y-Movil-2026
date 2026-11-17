"""Exporta guías Markdown a PDF legible sin servicios externos.

Ejecutar con el Python de .venv; dependencias en docs/requirements-documentos.txt.
No modifica los informes históricos de P1.
"""
from html import escape
from pathlib import Path
import re
import textwrap
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]


def fuente():
    candidatos = [
        (Path('C:/Windows/Fonts/arial.ttf'), Path('C:/Windows/Fonts/arialbd.ttf')),
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
    ]
    for normal, negrita in candidatos:
        if normal.exists() and negrita.exists():
            pdfmetrics.registerFont(TTFont('Guia', str(normal)))
            pdfmetrics.registerFont(TTFont('GuiaBold', str(negrita)))
            pdfmetrics.registerFontFamily('Guia', normal='Guia', bold='GuiaBold', italic='Guia', boldItalic='GuiaBold')
            return 'Guia', 'GuiaBold'
    return 'Helvetica', 'Helvetica-Bold'


def inline(text):
    text = escape(text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#245c72">\1</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text.replace('`', '')


def exportar(nombre):
    regular, bold = fuente()
    estilos = getSampleStyleSheet()
    for key in ['Normal', 'BodyText']:
        estilos[key].fontName = regular
        estilos[key].fontSize = 9
        estilos[key].leading = 12
        estilos[key].spaceAfter = 6
    for key, size in [('Title', 18), ('Heading1', 14), ('Heading2', 11.5), ('Heading3', 10)]:
        estilos[key].fontName = bold
        estilos[key].fontSize = size
        estilos[key].leading = size + 3
        estilos[key].spaceBefore = 10
        estilos[key].spaceAfter = 7
    celda = ParagraphStyle('Celda', parent=estilos['Normal'], fontSize=7.3, leading=9.4, spaceAfter=1)
    codigo = ParagraphStyle('Codigo', fontName=regular, fontSize=7.4, leading=9.4, backColor=colors.HexColor('#f0f3f5'), borderPadding=6)
    ruta = ROOT / 'docs' / (nombre + '.md')
    salida = ruta.with_suffix('.pdf')
    lineas = ruta.read_text(encoding='utf8').splitlines()
    story = []
    i = 0
    while i < len(lineas):
        s = lineas[i]
        if not s.strip():
            i += 1
            continue
        if s.startswith('<!-- SALTO_PAGINA'):
            story.append(PageBreak()); i += 1; continue
        if s.startswith('```'):
            bloque = []; i += 1
            while i < len(lineas) and not lineas[i].startswith('```'):
                bloque.extend(textwrap.wrap(lineas[i], width=105, replace_whitespace=False, drop_whitespace=False) or [''])
                i += 1
            story += [Preformatted(escape('\n'.join(bloque)), codigo), Spacer(1, 8)]
            i += 1; continue
        if s.startswith('|'):
            filas = []
            while i < len(lineas) and lineas[i].startswith('|'):
                raw = [c.strip() for c in lineas[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', c) for c in raw):
                    filas.append([Paragraph(inline(c), celda) for c in raw])
                i += 1
            columnas = len(filas[0])
            tabla = Table(filas, colWidths=[(A4[0]-88)/columnas]*columnas, repeatRows=1, hAlign=TA_LEFT)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dce7ea')),
                ('GRID', (0,0), (-1,-1), .3, colors.HexColor('#c2ccd0')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            story += [tabla, Spacer(1, 8)]
            continue
        heading = re.match(r'^(#{1,4}) (.+)', s)
        if heading:
            level = len(heading[1])
            story.append(Paragraph(inline(heading[2]), estilos['Title' if level == 1 else f'Heading{level-1}']))
            i += 1; continue
        parrafo = [s]; i += 1
        while i < len(lineas) and lineas[i].strip() and not re.match(r'^(#|\||```|<!--|\d+\. |\- )', lineas[i]):
            parrafo.append(lineas[i]); i += 1
        story.append(Paragraph(inline(' '.join(parrafo)), estilos['Normal']))

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont(regular, 8)
        canvas.setFillColor(colors.HexColor('#52646c'))
        canvas.drawString(44, 25, 'Lúmina Óptica · 22121280 · P1 y P2 · 17/11/2026')
        canvas.drawRightString(A4[0]-44, 25, f'Página {doc.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(str(salida), pagesize=A4, rightMargin=44, leftMargin=44, topMargin=35, bottomMargin=42,
                            title=ruta.stem.replace('_', ' '), author='Eduardo Osvaldo Rodríguez Gutiérrez · 22121280')
    doc.build(story, onFirstPage=pie, onLaterPages=pie)
    from pypdf import PdfReader
    pdf = PdfReader(salida)
    print(f'{salida.name}: {len(pdf.pages)} páginas; {salida.stat().st_size:,} bytes')
    if nombre == 'ANALISIS_PATRONES_P1_P2' and len(pdf.pages) != 2:
        raise RuntimeError('El análisis breve debe conservar dos páginas; revisar maquetación.')


if __name__ == '__main__':
    for archivo in ['DEFENSA_PROYECTOS_1_Y_2', 'ANALISIS_PATRONES_P1_P2', 'MATRIZ_PROYECTOS_1_Y_2']:
        exportar(archivo)
