#!/usr/bin/env python3
"""CAMPFIRE に「いま載っている」ページを、そのまま PDF に組む。

docs/campfire-live-page.txt は、CAMPFIRE のプレビュー画面から実際に取ってきた
掲載内容（本文・見出しブロック・図版の位置）。制作側の原稿ではなく、
掲載物そのものを写したもの。原稿（docs/campfire-project-body.md）とずれても
こちらが「いま公開されている内容」になる。

使い方:
    python3 tools/build-live-pdf.py            # 標準（和文フォントは非埋め込み）
    python3 tools/build-live-pdf.py --embed    # どの環境でも読める埋め込み版
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT / "docs" / "campfire-live-page.txt"
IMGDIR = Path.home() / "Desktop" / "VALHALLA_本文にはめる画像"
OUTDIR = Path("/tmp/valhalla_artifact")

INK = colors.HexColor("#141414")
SOFT = colors.HexColor("#4a4a4a")
BLACK = colors.HexColor("#0d0d0d")
LINE = colors.HexColor("#d8d4cc")
TINT = colors.HexColor("#f4f1ea")

MARGIN = 24 * mm
CW = A4[0] - MARGIN * 2

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
MIN, GO = "HeiseiMin-W3", "HeiseiKakuGo-W5"

EMBED_SRC = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def use_embedded_font() -> None:
    """和文フォントを PDF に実際に埋め込む。明朝ではなくなるが、どこでも読める。"""
    global MIN, GO
    from reportlab.pdfbase.ttfonts import TTFont
    if not Path(EMBED_SRC).exists():
        raise FileNotFoundError(f"埋め込み用フォントが見つかりません: {EMBED_SRC}")
    pdfmetrics.registerFont(TTFont("EmbedJP", EMBED_SRC))
    MIN = GO = "EmbedJP"


def styles():
    # wordWrap="CJK" で、行頭に句読点が落ちる禁則崩れを防ぐ
    def P(name, **kw):
        kw.setdefault("wordWrap", "CJK")
        return ParagraphStyle(name, **kw)
    return {
        "body": P("body", fontName=MIN, fontSize=10.2, leading=20,
                               textColor=INK, spaceAfter=7),
        "em": P("em", fontName=GO, fontSize=11, leading=21,
                             textColor=BLACK, spaceBefore=4, spaceAfter=9),
        "li": P("li", fontName=MIN, fontSize=9.8, leading=17.5,
                             textColor=INK, leftIndent=10, spaceAfter=3.5),
        "note": P("note", fontName=MIN, fontSize=8.8, leading=15.5,
                               textColor=SOFT, spaceAfter=4),
        "h": P("h", fontName=GO, fontSize=11.6, leading=19,
                            textColor=BLACK, spaceBefore=12, spaceAfter=6),
        "chEyebrow": P("chE", fontName=GO, fontSize=8, leading=13,
                                    textColor=colors.HexColor("#c9a961")),
        "chTitle": P("chT", fontName=GO, fontSize=15, leading=24,
                                  textColor=colors.white),
        "boxed": P("boxed", fontName=GO, fontSize=11, leading=20,
                                textColor=colors.white),
        "quote": P("q", fontName=MIN, fontSize=9.6, leading=18.5,
                                textColor=INK),
        "quoteBy": P("qb", fontName=GO, fontSize=9, leading=15,
                                  textColor=SOFT, alignment=2),
        "q": P("qq", fontName=GO, fontSize=10.2, leading=17,
                            textColor=BLACK),
        "a": P("aa", fontName=MIN, fontSize=9.6, leading=17.5,
                            textColor=INK),
        "cap": P("cap", fontName=MIN, fontSize=8.6, leading=14,
                              textColor=SOFT, alignment=TA_CENTER, spaceBefore=3),
        "sign": P("sg", fontName=GO, fontSize=12, leading=22,
                               textColor=BLACK, alignment=TA_CENTER,
                               spaceBefore=14, spaceAfter=6),
        "coverTitle": P("ct", fontName=GO, fontSize=19, leading=32,
                                     textColor=BLACK, alignment=TA_CENTER),
        "coverSub": P("cs", fontName=MIN, fontSize=10, leading=18,
                                   textColor=SOFT, alignment=TA_CENTER),
    }


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def picture(name: str, width=CW):
    """画像を段幅に合わせて置く。縦に長い絵はページに収まる高さで止める。"""
    p = IMGDIR / name
    if not p.exists():
        return None
    w, h = PILImage.open(p).size
    dw = width
    dh = dw * h / w
    cap = 100 * mm
    if dh > cap:
        dh, dw = cap, cap * w / h
    return Image(str(p), width=dw, height=dh, hAlign="CENTER")


def chapter_block(eyebrow: str, title: str, st):
    """CAMPFIRE ページ上の黒い章見出しブロックを、そのまま再現する。"""
    inner = [[Paragraph(esc(eyebrow), st["chEyebrow"])],
             [Paragraph(esc(title), st["chTitle"])]]
    t = Table(inner, colWidths=[CW - 16 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING", (0, 0), (-1, 0), 7 * mm),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7 * mm),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1.5 * mm),
    ]))
    outer = Table([[t]], colWidths=[CW])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 11 * mm), outer, Spacer(1, 7 * mm)]


def dark_box(text: str, st):
    t = Table([[Paragraph(esc(text), st["boxed"])]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 7 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5 * mm),
    ]))
    return [Spacer(1, 4 * mm), t, Spacer(1, 6 * mm)]


def quote_box(text: str, by: str, st):
    rows = [[Paragraph(esc(text), st["quote"])]]
    if by:
        rows.append([Paragraph(esc(by), st["quoteBy"])])
    t = Table(rows, colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("TOPPADDING", (0, 0), (-1, 0), 5 * mm),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 5 * mm),
    ]))
    return [Spacer(1, 4 * mm), t, Spacer(1, 6 * mm)]


def timeline(rows, st):
    flat = ParagraphStyle("flat", parent=st["li"], leftIndent=0)
    data = [[Paragraph(esc(a), st["q"]), Paragraph(esc(b), flat)] for a, b in rows]
    t = Table(data, colWidths=[34 * mm, CW - 34 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
    ]))
    return [Spacer(1, 3 * mm), t, Spacer(1, 5 * mm)]


def faq(qtext, atext, st):
    t = Table([[Paragraph(esc(qtext), st["q"])], [Paragraph(esc(atext), st["a"])]],
              colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TINT),
        ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("TOPPADDING", (0, 0), (-1, 0), 4.5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 1.5 * mm),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 4.5 * mm),
    ]))
    return [KeepTogether([t]), Spacer(1, 3 * mm)]


def build(out: Path) -> None:
    st = styles()
    lines = SRC.read_text(encoding="utf-8").splitlines()
    title = sub = ""
    flow = []
    pending_time = []

    def flush_time():
        if pending_time:
            flow.extend(timeline(list(pending_time), st))
            pending_time.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("#TIME:"):
            a, _, b = line[6:].partition("|")
            pending_time.append((a, b))
            continue
        flush_time()

        if line.startswith("#META:"):
            title = line[6:]
        elif line.startswith("#META2:"):
            sub = line[7:]
        elif line.startswith("#IMG:"):
            im = picture(line[5:])
            if im:
                flow.extend([Spacer(1, 3 * mm), im, Spacer(1, 6 * mm)])
            else:
                raise FileNotFoundError(f"画像が見つかりません: {line[5:]}")
        elif line.startswith("#VIDEO:"):
            t = Table([[Paragraph("▶　" + esc(line[7:]), st["cap"])]], colWidths=[CW])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), TINT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 6 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6 * mm),
            ]))
            flow.extend([t, Spacer(1, 6 * mm)])
        elif line.startswith("#CH:"):
            a, _, b = line[4:].partition("|")
            flow.extend(chapter_block(a, b, st))
        elif line.startswith("#BOX:"):
            flow.extend(dark_box(line[5:], st))
        elif line.startswith("#QUOTE:"):
            a, _, b = line[7:].partition("|")
            flow.extend(quote_box(a, b, st))
        elif line.startswith("#EM:"):
            flow.append(Paragraph(esc(line[4:]), st["em"]))
        elif line.startswith("#H:"):
            flow.append(Paragraph(esc(line[3:]), st["h"]))
        elif line.startswith("#LI:"):
            flow.append(Paragraph("・" + esc(line[4:]), st["li"]))
        elif line.startswith("#NOTE:"):
            flow.append(Paragraph(esc(line[6:]), st["note"]))
        elif line.startswith("#Q:"):
            q = line[3:]
            flow.append(("__Q__", q))
        elif line.startswith("#A:"):
            q = flow.pop()[1]
            flow.extend(faq(q, line[3:], st))
        elif line.startswith("#SIGN:"):
            a, _, b = line[6:].partition("|")
            flow.append(Paragraph(esc(a), st["sign"]))
            flow.append(Paragraph(esc(b), st["coverSub"]))
        else:
            flow.append(Paragraph(esc(line), st["body"]))
    flush_time()

    cover = [Spacer(1, 52 * mm)]
    mv = picture("IMAGE-01.jpg", CW)
    if mv:
        cover.append(mv)
    cover += [Spacer(1, 12 * mm),
              Paragraph(esc(title), st["coverTitle"]),
              Spacer(1, 5 * mm),
              Paragraph(esc(sub), st["coverSub"]),
              Spacer(1, 3 * mm),
              Paragraph("CAMPFIRE｜クラウドファンディング", st["coverSub"]),
              Spacer(1, 26 * mm)]

    def deco(canvas, doc):
        canvas.saveState()
        canvas.setFont(GO, 7.2)
        canvas.setFillColor(colors.HexColor("#9a958c"))
        if doc.page > 1:
            canvas.drawString(MARGIN, 13 * mm, "VALHALLA CHARITY LIVE｜CAMPFIRE 掲載ページ")
            canvas.drawRightString(A4[0] - MARGIN, 13 * mm, str(doc.page - 1))
        canvas.restoreState()

    doc = BaseDocTemplate(str(out), pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=20 * mm, bottomMargin=20 * mm,
                          title=title, author="VALHALLA")
    frame = Frame(MARGIN, 20 * mm, CW, A4[1] - 40 * mm, id="f",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=deco)])
    from reportlab.platypus import PageBreak
    doc.build(cover + [PageBreak()] + flow)
    print(f"{out}  {out.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    OUTDIR.mkdir(parents=True, exist_ok=True)
    if "--embed" in sys.argv:
        use_embedded_font()
        build(OUTDIR / "campfire-live-page-embed.pdf")
    else:
        build(OUTDIR / "campfire-live-page.pdf")
