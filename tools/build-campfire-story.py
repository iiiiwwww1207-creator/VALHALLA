#!/usr/bin/env python3
"""docs/campfire-live-page.txt を、CAMPFIRE のストーリー欄へ流し込む HTML に組む。

見た目は、いま掲載されている本文から実測した装飾をそのまま使う。
エディタ（Froala）は class を残さないので、すべてインラインの style で書く。

    章見出し   黒帯 + 左の赤い縦線
    小見出し   18px の太字
    注記       #6b6868 の 14px
    質問       薄い桃色の帯
    答え       左右に余白だけ
    引用       左に赤い縦線 ／ 署名は右寄せ
    囲み       うすい桃色の面
    画像       中央寄せ・幅100%

画像の URL は tools/campfire-image-urls.json から読む。
差し替えた図版は、先に上げ直して URL を書き換えること。

使い方: python3 tools/build-campfire-story.py
出力  : /tmp/valhalla_artifact/story_body.html
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "campfire-live-page.txt"
URLS = ROOT / "tools" / "campfire-image-urls.json"
OUT = Path("/tmp/valhalla_artifact/story_body.html")

VIDEOS = ["3hI1awQ6Txk", "nnLM_4LU9UI"]   # 本文の #VIDEO: と同じ順

S_CH    = "background-color:#0a0709;border-left:6px solid #c1121f;padding:18px 22px;"
S_EYE   = "color:#d9949a;font-size:12px;letter-spacing:2px;"
S_TITLE = "color:#f5efe4;font-size:22px;"
S_NOTE  = "color:#6b6868;font-size:14px;"
S_Q     = "background-color:#f3ecec;padding:12px 16px;"
S_A     = "padding:0 16px 10px;"
S_BOX   = "background-color:#fbf4f4;padding:16px 18px;"
S_H     = "font-size:18px;"
S_QUOTE = "border-left:3px solid #c1121f;padding-left:14px;"
S_BY    = "text-align:right;"
S_CENT  = "text-align:center;"


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def build() -> str:
    urls = json.loads(URLS.read_text(encoding="utf-8"))
    lines = SRC.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    items: list[str] = []
    pending_q: str | None = None
    vi = 0
    n_img = 0

    def flush():
        nonlocal items
        if items:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            items = []

    for raw in lines:
        line = raw.rstrip()

        if line.startswith("#LI:"):
            items.append(esc(line[4:]))
            continue
        flush()

        if not line or line.startswith("#META"):
            continue

        if line.startswith("#IMG:"):
            name = line[5:]
            if name not in urls:
                raise KeyError(f"画像の URL が未登録です: {name}")
            n_img += 1
            out.append(f'<p style="{S_CENT}"><img src="{urls[name]}" alt="{esc(name)}" '
                       f'class="fr-fic fr-dib" style="width:100%;"></p>')
        elif line.startswith("#VIDEO:"):
            vid = VIDEOS[vi]
            vi += 1
            out.append('<div class="fr-video fr-dvb fr-draggable" contenteditable="false">'
                       f'<iframe width="640" height="360" src="https://www.youtube.com/embed/{vid}" '
                       'frameborder="0" allowfullscreen="" class="fr-draggable"></iframe></div>')
        elif line.startswith("#CH:"):
            a, _, b = line[4:].partition("|")
            out.append(f'<p style="{S_CH}"><span style="{S_EYE}">{esc(a)}</span><br>'
                       f'<strong style="{S_TITLE}">{esc(b)}</strong></p>')
        elif line.startswith("#BOX:"):
            out.append(f'<p style="{S_BOX}"><strong>{esc(line[5:])}</strong></p>')
        elif line.startswith("#EM:"):
            out.append(f"<p><strong>{esc(line[4:])}</strong></p>")
        elif line.startswith("#H:"):
            out.append(f'<p><strong style="{S_H}">{esc(line[3:])}</strong></p>')
        elif line.startswith("#NOTE:"):
            out.append(f'<p style="{S_NOTE}">{esc(line[6:])}</p>')
        elif line.startswith("#TIME:"):
            a, _, b = line[6:].partition("|")
            out.append(f"<p><strong>{esc(a)}</strong>　{esc(b)}</p>")
        elif line.startswith("#QUOTE:"):
            a, _, b = line[7:].partition("|")
            out.append(f'<p style="{S_QUOTE}">{esc(a)}</p>')
            if b:
                out.append(f'<p style="{S_BY}">{esc(b)}</p>')
        elif line.startswith("#SIGN:"):
            a, _, b = line[6:].partition("|")
            out.append(f'<p style="{S_CENT}"><strong>{esc(a)}</strong><br>{esc(b)}</p>')
        elif line.startswith("#Q:"):
            pending_q = line[3:]
        elif line.startswith("#A:"):
            out.append(f'<p style="{S_Q}"><strong>{esc(pending_q or "")}</strong></p>')
            out.append(f'<p style="{S_A}">A. {esc(line[3:])}</p>')
            pending_q = None
        else:
            out.append(f"<p>{esc(line)}</p>")

    flush()
    if vi != len(VIDEOS):
        raise RuntimeError(f"動画の数が合いません: 本文 {vi} / 登録 {len(VIDEOS)}")
    if pending_q:
        raise RuntimeError(f"答えのない質問が残っています: {pending_q}")

    doc = "".join(out)

    # 出してから気づいても直せないので、ここで止める
    for ng in ("無料", "やしろ学園", "S席", "最前列席", "シンプル応援",
               "150,000", "限定100口", "第三者へ資金を移す", "が活用します"):
        if ng in doc:
            raise RuntimeError(f"旧表記が残っています: {ng}")
    plain = re.sub(r"<[^>]+>", "", doc)
    if "#" in plain:
        raise RuntimeError("変換し損ねた記法（#）が本文に残っています")

    print(f"画像 {n_img} 点 ／ 動画 {vi} 本 ／ {len(doc):,} 文字")
    return doc


def main() -> None:
    doc = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
