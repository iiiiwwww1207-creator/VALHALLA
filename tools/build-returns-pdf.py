#!/usr/bin/env python3
"""リターン品一覧（docs/campfire-returns-list.html）を印刷用の PDF に組む。

打ち合わせに紙で持っていくため。macOS には HTML→PDF の変換フィルタが無く
（cupsfilter は text/html を受け付けない）、pandoc も入っていないので、
一覧の HTML を読み取って reportlab で組み直している。

HTML はこちらで書いたものなので、構造（h2 / .lead / .sum / .course / ol.ask）は
分かっている前提で拾う。文言を直すときは HTML 側を直せば、この PDF も追従する。

使い方: python3 tools/build-returns-pdf.py
出力  : docs/campfire-returns-list.pdf
"""
import html as htmllib
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "campfire-returns-list.html"
OUT = ROOT / "docs" / "campfire-returns-list.pdf"

pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
MIN, GO = "HeiseiMin-W3", "HeiseiKakuGo-W5"

INK = colors.HexColor("#191419")
SUB = colors.HexColor("#6B6169")
CRIMSON = colors.HexColor("#C1121F")
DEEP = colors.HexColor("#8E1019")
RULE = colors.HexColor("#E7DED6")
BAND = colors.HexColor("#F3E9E6")
OK = colors.HexColor("#2E6E4E")
WARN = colors.HexColor("#9A5B00")

PW, PH = A4
MARGIN = 18 * mm
CW = PW - MARGIN * 2

S = {
    "h2": ParagraphStyle("h2", fontName=MIN, fontSize=13.5, leading=20, textColor=INK,
                         spaceBefore=18, spaceAfter=6),
    "lead": ParagraphStyle("lead", fontName=GO, fontSize=8.8, leading=15, textColor=SUB,
                           leftIndent=8, borderPadding=0, spaceAfter=8),
    "cell": ParagraphStyle("cell", fontName=GO, fontSize=8.6, leading=13.6, textColor=INK),
    "note": ParagraphStyle("note", fontName=GO, fontSize=7.8, leading=12, textColor=SUB),
    "when": ParagraphStyle("when", fontName=GO, fontSize=7.8, leading=12, textColor=SUB),
    "grp": ParagraphStyle("grp", fontName=GO, fontSize=8, leading=12, textColor=DEEP),
    "sumh": ParagraphStyle("sumh", fontName=GO, fontSize=7.6, leading=11, textColor=SUB),
    "sum": ParagraphStyle("sum", fontName=GO, fontSize=8.4, leading=12.5, textColor=INK),
    "ask": ParagraphStyle("ask", fontName=GO, fontSize=8.8, leading=14.5, textColor=INK),
    "askn": ParagraphStyle("askn", fontName=GO, fontSize=7.9, leading=13, textColor=SUB),
    "foot": ParagraphStyle("foot", fontName=GO, fontSize=7.4, leading=12, textColor=SUB),
}

TAG = {"fix": ("確定", OK), "tbd": ("要確定", WARN)}


def text_of(frag: str, keep_tags: bool = True) -> str:
    """タグを落として本文だけにする。<b> だけは reportlab 用に残す。"""
    frag = re.sub(r'<span class="tag (\w+)">.*?</span>',
                  lambda m: f'　<font color="{TAG[m.group(1)][1].hexval()}">'
                            f'［{TAG[m.group(1)][0]}］</font>' if m.group(1) in TAG else "",
                  frag, flags=re.S)
    frag = re.sub(r'<span class="tbd">(.*?)</span>',
                  rf'<font color="{WARN.hexval()}">\1</font>', frag, flags=re.S)
    frag = re.sub(r"<br\s*/?>", " ", frag)
    if keep_tags:
        frag = re.sub(r"<(?!/?b\b|/?font\b)[^>]+>", "", frag)
    else:
        frag = re.sub(r"<[^>]+>", "", frag)
    out = re.sub(r"\s+", " ", htmllib.unescape(frag)).strip()
    # reportlab も & を実体参照として読むので、素の & は戻しておく（Q&A 対策）
    return re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+);)", "&amp;", out)


def cells(row: str):
    return re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)


def build_sum(block: str):
    head = [Paragraph(text_of(h), S["sumh"])
            for h in re.findall(r"<th[^>]*>(.*?)</th>", block, re.S)]
    rows = [head]
    styles = [("GRID", (0, 0), (-1, -1), 0.4, RULE),
              ("BACKGROUND", (0, 0), (-1, 0), BAND),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("LEFTPADDING", (0, 0), (-1, -1), 5),
              ("RIGHTPADDING", (0, 0), (-1, -1), 5),
              ("TOPPADDING", (0, 0), (-1, -1), 4),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    body = block[block.index("<tbody>"):]
    for i, row in enumerate(re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S), start=1):
        rows.append([Paragraph(text_of(c), S["sum"]) for c in cells(row)])
        if 'class="total"' in row:
            styles.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t = Table(rows, colWidths=[CW * w for w in (.20, .14, .14, .12, .26, .14)], repeatRows=1)
    t.setStyle(TableStyle(styles))
    return t


def build_course(block: str):
    flow = []
    head = re.search(r'<div class="chead">(.*?)</div>\s*<table', block, re.S)
    if head:
        h = head.group(1)
        name = text_of(re.search(r'class="name">(.*?)</span>', h, re.S).group(1))
        price = text_of(re.search(r'class="price">(.*?)</span>', h, re.S).group(1))
        qty_m = re.search(r'class="qty">(.*?)</span>', h, re.S)
        qty = text_of(qty_m.group(1)) if qty_m else ""
        t = Table([[Paragraph(f'<b>{name}</b>　<font size="11">{price}</font>',
                              ParagraphStyle("cn", parent=S["cell"], fontName=MIN,
                                             fontSize=10.5, leading=15)),
                    Paragraph(qty, ParagraphStyle("cq", parent=S["note"], alignment=2))]],
                  colWidths=[CW * .45, CW * .55])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BAND),
                               ("BOX", (0, 0), (-1, -1), 0.4, RULE),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 7),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                               ("TOPPADDING", (0, 0), (-1, -1), 5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        flow.append(t)

    rows, styles = [], [("GRID", (0, 0), (-1, -1), 0.4, RULE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    # class は開始タグ側にあるので、タグごと拾わないとグループ行を判定できない
    for open_tag, row in re.findall(r"(<tr[^>]*>)(.*?)</tr>", block, re.S):
        if 'class="grp"' in open_tag:
            rows.append([Paragraph(f'<b>{text_of(cells(row)[0])}</b>', S["grp"]), ""])
            styles += [("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), BAND),
                       ("SPAN", (0, len(rows) - 1), (-1, len(rows) - 1))]
            continue
        cs = cells(row)
        if len(cs) < 2:
            continue
        what = cs[0]
        note = re.search(r'<span class="note">(.*?)</span>', what, re.S)
        main = text_of(re.sub(r'<span class="note">.*?</span>', "", what, flags=re.S))
        para = [Paragraph(main, S["cell"])]
        if note:
            para.append(Paragraph(text_of(note.group(1)), S["note"]))
        rows.append([para, Paragraph(text_of(cs[1]), S["when"])])
    if rows:
        t = Table(rows, colWidths=[CW * .76, CW * .24])
        t.setStyle(TableStyle(styles))
        flow.append(t)
    flow.append(Spacer(1, 10))
    return flow


def build_ask(block: str):
    out = []
    for i, li in enumerate(re.findall(r"<li>(.*?)</li>", block, re.S), start=1):
        b = re.search(r"<b>(.*?)</b>", li, re.S)
        rest = re.sub(r"<b>.*?</b>", "", li, count=1, flags=re.S)
        out.append(KeepTogether([
            Paragraph(f'<b>{i}. {text_of(b.group(1)) if b else ""}</b>', S["ask"]),
            Paragraph(text_of(rest), S["askn"]),
            Spacer(1, 7)]))
    return out


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    body = src[src.index('<div class="wrap">'):]

    story = []
    pattern = re.compile(
        r'<h2>(?P<h2>.*?)</h2>'
        r'|<table class="sum">(?P<sum>.*?)</table>'
        # course は中に chead の div を1つ持つので、最初の </div> で切ると本体を取り逃す。
        # 各 course に table はちょうど1つなので、そこを終端にする。
        r'|<div class="course(?: feat)?">(?P<course>.*?)</table>\s*</div>'
        r'|<ol class="ask">(?P<ask>.*?)</ol>'
        r'|<p class="lead"[^>]*>(?P<lead>.*?)</p>'
        r'|<p class="foot">(?P<foot>.*?)</p>'
        r'|<p style="color:var\(--sub\)[^>]*>(?P<小>.*?)</p>', re.S)
    for m in pattern.finditer(body):
        if m.group("h2"):
            story += [Paragraph(text_of(m.group("h2")), S["h2"]),
                      Table([[""]], colWidths=[CW], rowHeights=[1.4],
                            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), INK)])),
                      Spacer(1, 7)]
        elif m.group("sum"):
            story += [build_sum(m.group(0)), Spacer(1, 6)]
        elif m.group("course") is not None:
            story += build_course(m.group("course"))
        elif m.group("ask"):
            story += build_ask(m.group("ask"))
        elif m.group("lead"):
            story += [Paragraph(text_of(m.group("lead")), S["lead"])]
        elif m.group("小"):
            story += [Paragraph(text_of(m.group("小")), S["note"]), Spacer(1, 4)]
        elif m.group("foot"):
            story += [Spacer(1, 12), Paragraph(text_of(m.group("foot")), S["foot"])]

    def cover(canvas, doc):
        canvas.saveState()
        if canvas.getPageNumber() == 1:
            canvas.setFillColor(DEEP)
            canvas.rect(0, PH - 34 * mm, PW, 34 * mm, stroke=0, fill=1)
            canvas.setFillColor(colors.HexColor("#FBF6F2"))
            canvas.setFont(GO, 7.6)
            canvas.drawString(MARGIN, PH - 13 * mm, "V A L H A L L A   C H A R I T Y   L I V E ／ C A M P F I R E")
            canvas.setFont(MIN, 19)
            canvas.drawString(MARGIN, PH - 22 * mm, "リターン品一覧")
            canvas.setFont(GO, 7.8)
            canvas.drawString(MARGIN, PH - 28.5 * mm,
                              "2026年10月18日（日）渋谷　OPEN 19:00 ／ 受付締切 19:25 ／ "
                              "START 19:30 ／ 終演 21:10　ご支援に対してお渡しするもの・体験のすべて")
        canvas.setFillColor(SUB)
        canvas.setFont(GO, 7)
        canvas.drawRightString(PW - MARGIN, 10 * mm, str(canvas.getPageNumber()))
        canvas.drawString(MARGIN, 10 * mm, "VALHALLA CHARITY LIVE ／ リターン品一覧（2026年9月8日時点）")
        canvas.restoreState()

    doc = BaseDocTemplate(str(OUT), pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title="リターン品一覧 ／ VALHALLA CHARITY LIVE")
    first = Frame(MARGIN, MARGIN, CW, PH - 40 * mm - MARGIN, id="first")
    rest = Frame(MARGIN, MARGIN, CW, PH - MARGIN * 2 - 6 * mm, id="rest")
    doc.addPageTemplates([PageTemplate(id="first", frames=[first], onPage=cover),
                          PageTemplate(id="rest", frames=[rest], onPage=cover)])
    doc.build(story)
    print(f"{OUT}　{OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
