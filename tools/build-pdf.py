#!/usr/bin/env python3
"""CAMPFIRE 本文ドラフトを、送付用の PDF に組む。

送付先がリンクを開けない場合や、印刷して配りたい場合のための形式。
本文は tools/build-artifact.py と同じ「送付用」（制作側あての注記を除いた版）を使う。

使い方: python3 tools/build-pdf.py
出力  : /tmp/valhalla_artifact/campfire-draft.pdf
"""
import importlib.util
import io
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image,
                                PageTemplate, PageBreak, Paragraph, Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = Path("/tmp/valhalla_artifact/campfire-draft.pdf")

def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, HERE / fn)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

prev = _load("prev", "build-campfire-preview.py")
art = _load("art", "build-artifact.py")

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
MIN, GO = "HeiseiMin-W3", "HeiseiKakuGo-W5"

INK = colors.HexColor("#171216")
SUB = colors.HexColor("#6B6469")
CRIMSON = colors.HexColor("#C1121F")
DEEP = colors.HexColor("#8E1019")
LINE = colors.HexColor("#E7DFDF")

PW, PH = A4
MARGIN = 22 * mm
CW = PW - MARGIN * 2

S = {
    "h2": ParagraphStyle("h2", fontName=MIN, fontSize=15, leading=24, textColor=INK,
                         spaceBefore=26, spaceAfter=2),
    "p": ParagraphStyle("p", fontName=GO, fontSize=9.6, leading=18.5, textColor=INK,
                        spaceAfter=9),
    "li": ParagraphStyle("li", fontName=GO, fontSize=9.6, leading=18.5, textColor=INK,
                         leftIndent=12, bulletIndent=2, spaceAfter=4),
    "q": ParagraphStyle("q", fontName=MIN, fontSize=9.6, leading=19, textColor=INK,
                        leftIndent=12, spaceAfter=8),
    "cap": ParagraphStyle("cap", fontName=GO, fontSize=7.6, leading=12, textColor=SUB,
                          alignment=TA_CENTER, spaceBefore=4, spaceAfter=14),
}


# 日本語CIDフォントに É / Ø が無く、代替グリフの送り幅がずれて字間が空くため、
# その2文字だけ欧文フォントで出す
ACCENT = str.maketrans({"É": '<font name="Helvetica">É</font>',
                        "Ø": '<font name="Helvetica">Ø</font>'})


def esc(t: str) -> str:
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.translate(ACCENT)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"\1", t)
    t = re.sub(r"〔(.+?)〕", r'<font color="#6B6469">\1</font>', t)
    return t


def picture(path: str):
    src = ROOT / path
    im = PILImage.open(src).convert("RGB")
    if im.width > 1400:
        im = im.resize((1400, round(im.height * 1400 / im.width)), PILImage.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True)
    buf.seek(0)
    return Image(buf, width=CW, height=CW * im.height / im.width)


def build_story(body: str):
    story, para, quote, in_q = [], [], [], False

    def flush_p():
        if para:
            story.append(Paragraph(esc("".join(para)), S["p"]))
            para.clear()

    def flush_q():
        nonlocal in_q
        if quote:
            story.append(Paragraph(esc("".join(quote)), S["q"]))
            quote.clear()
        in_q = False

    for raw in body.split("\n"):
        t = raw.strip()
        if not t:
            flush_p()
            if in_q:
                flush_q()
            continue
        if t.startswith("### "):
            flush_p(); flush_q()
            story.append(Paragraph(esc(t[4:]), S["h2"]))
            story.append(HRFlowable(width="100%", thickness=1, color=INK, spaceAfter=10))
            continue
        m = re.match(r"^【画像】(.*?)`([^`]+)`(.*)$", t)
        if m:
            flush_p(); flush_q()
            story.append(picture(m.group(2)))
            cap = (m.group(1) + " " + m.group(3)).strip(" （）()")
            story.append(Paragraph(esc(cap) if cap else "&nbsp;", S["cap"]))
            continue
        if t.startswith("【動画】"):
            flush_p(); flush_q()
            u = re.search(r"https?://\S+", t)
            url = u.group(0) if u else ""
            box = Table([[Paragraph(
                f'<b>BORN IN DESPAIR -MV-【VALHALLA】</b><br/>'
                f'<font size="8" color="#6B6469"><link href="{url}">{url}</link></font>',
                S["p"])]], colWidths=[CW])
            box.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
            story.append(box); story.append(Spacer(1, 14))
            continue
        if set(t) <= {"─"} and len(t) > 3:
            flush_p(); flush_q()
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=10))
            continue
        if t.startswith("> "):
            flush_p()
            in_q = True
            quote.append(t[2:])
            continue
        if t == ">":
            if quote:
                story.append(Paragraph(esc("".join(quote)), S["q"]))
                quote.clear()
            continue
        if in_q:
            flush_q()
        if t.startswith("- ") or t.startswith("・"):
            flush_p()
            story.append(Paragraph(esc(t[2:] if t.startswith("- ") else t[1:]),
                                   S["li"], bulletText="・"))
            continue
        if re.match(r"^\d+\. ", t):
            flush_p()
            story.append(Paragraph(esc(t), S["li"]))
            continue
        para.append(t)
    flush_p(); flush_q()
    return story


def cover(c, doc):
    c.saveState()
    c.setFillColor(DEEP)
    c.rect(0, PH - 62 * mm, PW, 62 * mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#F0B9B6"))
    c.setFont(GO, 8)
    c.drawString(MARGIN, PH - 22 * mm, "C A M P F I R E ページ本文 ドラフト")
    c.setFillColor(colors.HexColor("#FBF3F2"))
    c.setFont(MIN, 25)
    c.drawString(MARGIN, PH - 35 * mm, "ビジュアル系文化の、再興。")
    c.setFillColor(colors.HexColor("#EBC4C1"))
    c.setFont(GO, 9)
    c.drawString(MARGIN, PH - 46 * mm, "VALHALLA CHARITY LIVE ／ 2026年10月18日（日）")
    x = MARGIN
    for part, fnt in (("C", GO), ("É", "Helvetica"),
                      (" LA VI TOKYO（渋谷・17F）　OPEN 19:00 ／ START 19:30 ／ 終演 21:30", GO)):
        c.setFont(fnt, 9)
        c.drawString(x, PH - 52 * mm, part)
        x += c.stringWidth(part, fnt, 9)
    c.restoreState()
    footer(c, doc)


def footer(c, doc):
    c.saveState()
    c.setFont(GO, 7.5)
    c.setFillColor(SUB)
    c.drawCentredString(PW / 2, 12 * mm, str(c.getPageNumber()))
    c.restoreState()


def main() -> None:
    md = open(ROOT / prev.SRC, encoding="utf-8").read()
    body = art.for_sharing(prev.extract_body(md))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4,
                          title="VALHALLA CHARITY LIVE 本文ドラフト",
                          author="VALHALLA",
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=20 * mm)
    first = Frame(MARGIN, 20 * mm, CW, PH - 62 * mm - 20 * mm - 6 * mm, id="first")
    rest = Frame(MARGIN, 20 * mm, CW, PH - MARGIN - 20 * mm, id="rest")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[first], onPage=cover),
        PageTemplate(id="body", frames=[rest], onPage=footer),
    ])

    story = [Paragraph(
        '制作中のドラフトです。グレーの箇所は現在調整中で、確定しだい差し替えます。'
        'CAMPFIRE のページには、この文章と図版をそのまま掲載する想定です。',
        ParagraphStyle("lead", fontName=GO, fontSize=8.6, leading=15, textColor=SUB,
                       spaceAfter=6))]
    story.append(Spacer(1, 6))
    from reportlab.platypus import NextPageTemplate
    story.append(NextPageTemplate("body"))
    story += build_story(body)
    doc.build(story)
    print(f"{OUT}  {OUT.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
