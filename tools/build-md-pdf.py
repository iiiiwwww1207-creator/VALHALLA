#!/usr/bin/env python3
"""先方に送る Markdown を、そのまま渡せる A4 の PDF に組む。

打ち合わせの回答書・確認事項など、体裁を整えて渡したい短めの文書向け。
本文ページ（build-live-pdf.py）とは別物で、図版は扱わない。

使い方: python3 tools/build-md-pdf.py <入力.md> <出力.pdf> [表紙タイトル]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
MIN, GO = "HeiseiMin-W3", "HeiseiKakuGo-W5"

M = 24 * mm
CW = A4[0] - M * 2
INK = colors.HexColor("#141414")
SOFT = colors.HexColor("#555555")
TINT = colors.HexColor("#f4f1ea")
LINE = colors.HexColor("#d8d4cc")
BLACK = colors.HexColor("#0d0d0d")


def P(name, **kw):
    kw.setdefault("wordWrap", "CJK")   # 行頭に句読点が落ちる禁則崩れを防ぐ
    return ParagraphStyle(name, **kw)


S = {
    "b": P("b", fontName=MIN, fontSize=10, leading=19, textColor=INK, spaceAfter=6),
    "h1": P("h1", fontName=GO, fontSize=14, leading=24, textColor=colors.white),
    "h2": P("h2", fontName=GO, fontSize=11.5, leading=19, textColor=BLACK,
            spaceBefore=10, spaceAfter=5),
    "li": P("li", fontName=MIN, fontSize=9.6, leading=17, textColor=INK,
            leftIndent=10, spaceAfter=3),
    "q": P("q", fontName=MIN, fontSize=9.4, leading=16.5, textColor=SOFT),
    "th": P("th", fontName=GO, fontSize=9, leading=15, textColor=BLACK),
    "td": P("td", fontName=MIN, fontSize=9, leading=15, textColor=INK),
    "title": P("t", fontName=GO, fontSize=16, leading=28, textColor=BLACK),
}


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(t: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r'<font name="%s">\1</font>' % GO, esc(t))


def build(src: Path, out: Path, title: str) -> None:
    flow, tbl = [], []

    def flush_tbl():
        nonlocal tbl
        if not tbl:
            return
        rows = [[Paragraph(inline(c), S["th"] if i == 0 else S["td"]) for c in r]
                for i, r in enumerate(tbl)]
        n = max(len(r) for r in rows)
        rows = [r + [Paragraph("", S["td"])] * (n - len(r)) for r in rows]
        t = Table(rows, colWidths=[CW / n] * n)
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, 0), TINT),
            ("GRID", (0, 0), (-1, -1), 0.4, LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 2.6 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6 * mm),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ]))
        flow.extend([Spacer(1, 3 * mm), t, Spacer(1, 5 * mm)])
        tbl = []

    for raw in src.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            tbl.append(cells)
            continue
        flush_tbl()
        if not line:
            continue
        if line.startswith("---"):
            flow.append(Spacer(1, 4 * mm))
        elif line.startswith("# "):
            t = Table([[Paragraph(inline(line[2:]), S["h1"])]], colWidths=[CW])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BLACK),
                ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
            ]))
            flow.extend([Spacer(1, 7 * mm), t, Spacer(1, 6 * mm)])
        elif line.startswith("## "):
            flow.append(Paragraph(inline(line[3:]), S["h2"]))
        elif line.startswith("### "):
            flow.append(Paragraph(inline(line[4:]), S["h2"]))
        elif line.startswith("> "):
            t = Table([[Paragraph(inline(line[2:]), S["q"])]], colWidths=[CW])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), TINT),
                ("LINEBEFORE", (0, 0), (0, -1), 2, BLACK),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.4 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4 * mm),
            ]))
            flow.extend([t, Spacer(1, 1.4 * mm)])
        elif line.startswith(("- ", "* ")):
            flow.append(Paragraph("・" + inline(line[2:]), S["li"]))
        elif re.match(r"^\d+\. ", line):
            flow.append(Paragraph(inline(line), S["li"]))
        elif line.startswith("※"):
            flow.append(Paragraph(inline(line), S["q"]))
        else:
            flow.append(Paragraph(inline(line), S["b"]))
    flush_tbl()

    def deco(canvas, doc):
        canvas.saveState()
        canvas.setFont(GO, 7.2)
        canvas.setFillColor(colors.HexColor("#9a958c"))
        canvas.drawRightString(A4[0] - M, 13 * mm, str(doc.page))
        canvas.restoreState()

    doc = BaseDocTemplate(str(out), pagesize=A4, leftMargin=M, rightMargin=M,
                          topMargin=20 * mm, bottomMargin=20 * mm, title=title)
    doc.addPageTemplates([PageTemplate(id="p", frames=[
        Frame(M, 20 * mm, CW, A4[1] - 40 * mm, id="f", leftPadding=0,
              rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
    head = [Paragraph(esc(title), S["title"]), Spacer(1, 4 * mm)]
    doc.build(head + flow)
    print(f"{out}  {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    build(src, out, title)
