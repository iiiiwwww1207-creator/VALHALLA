#!/usr/bin/env python3
"""図版を全部入れたあとの CAMPFIRE ページを、そのまま1枚のHTMLで見られるようにする。

CAMPFIRE に上げる前に「入れたらどう見えるか」を通しで確かめるためのもの。
見た目の数値（段幅・色・字送り・余白）は、実際の掲載ページから実測して写した。

画像は data URI で埋め込む。動画は外部を読めないので、
YouTube のサムネイルを埋め込んで、押すと YouTube が開くようにする。

使い方: python3 tools/build-page-preview.py
出力  : /tmp/valhalla_artifact/campfire-page-preview.html
"""
from __future__ import annotations

import base64
import html
import io
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "campfire-live-page.txt"
STAMP = "2026年9月18日 18:10 時点"
IMGDIR = Path.home() / "Desktop" / "VALHALLA_本文にはめる画像"
THUMBS = Path("/tmp/valhalla_artifact/thumbs")
OUT = Path("/tmp/valhalla_artifact/campfire-page-preview.html")

# 動画は掲載順に対応させる
VIDEOS = ["3hI1awQ6Txk", "nnLM_4LU9UI"]

# CAMPFIRE 掲載ページから実測した値
COLUMN = 656


def data_uri(path: Path, width: int = 900, quality: int = 80) -> str:
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)),
                       Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def esc(t: str) -> str:
    return html.escape(t)


def build() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    body: list[str] = []
    times: list[tuple[str, str]] = []
    pending_q: str | None = None
    vi = 0
    n_img = 0

    def flush_times():
        nonlocal times
        if not times:
            return
        rows = "".join(
            f'<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in times)
        body.append(f'<table class="tl">{rows}</table>')
        times = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("#TIME:"):
            a, _, b = line[6:].partition("|")
            times.append((a, b))
            continue
        flush_times()
        if not line:
            continue

        if line.startswith("#META"):
            continue
        if line.startswith("#IMG:"):
            name = line[5:]
            p = IMGDIR / name
            if not p.exists():
                raise FileNotFoundError(f"画像がありません: {name}")
            new = False
            n_img += 1
            tag = '<span class="badge">今回ふやした図版</span>' if new else ""
            body.append(f'<figure class="{"fig new" if new else "fig"}">'
                        f'<img src="{data_uri(p)}" alt="{esc(name)}">{tag}</figure>')
        elif line.startswith("#VIDEO:"):
            vid = VIDEOS[vi] if vi < len(VIDEOS) else VIDEOS[-1]
            vi += 1
            th = THUMBS / f"{vid}.jpg"
            src = data_uri(th, width=900, quality=78) if th.exists() else ""
            body.append(
                f'<a class="video" href="https://www.youtube.com/watch?v={vid}" '
                f'target="_blank" rel="noopener">'
                f'<img src="{src}" alt="{esc(line[7:])}">'
                f'<span class="play"></span>'
                f'<span class="vcap">{esc(line[7:])}</span></a>')
        elif line.startswith("#CH:"):
            a, _, b = line[4:].partition("|")
            body.append(f'<div class="ch"><p class="eyebrow">{esc(a)}</p>'
                        f'<p class="chtitle">{esc(b)}</p></div>')
        elif line.startswith("#BOX:"):
            body.append(f'<p class="band">{esc(line[5:])}</p>')
        elif line.startswith("#QUOTE:"):
            a, _, b = line[7:].partition("|")
            by = f'<span class="by">{esc(b)}</span>' if b else ""
            body.append(f'<blockquote>{esc(a)}{by}</blockquote>')
        elif line.startswith("#EM:"):
            body.append(f'<p class="em">{esc(line[4:])}</p>')
        elif line.startswith("#H:"):
            body.append(f'<h3>{esc(line[3:])}</h3>')
        elif line.startswith("#LI:"):
            body.append(f'<p class="li">{esc(line[4:])}</p>')
        elif line.startswith("#NOTE:"):
            body.append(f'<p class="note">{esc(line[6:])}</p>')
        elif line.startswith("#Q:"):
            pending_q = line[3:]
        elif line.startswith("#A:"):
            body.append(f'<p class="q">{esc(pending_q or "")}</p>'
                        f'<p class="a">A. {esc(line[3:])}</p>')
            pending_q = None
        elif line.startswith("#SIGN:"):
            a, _, b = line[6:].partition("|")
            body.append(f'<p class="sign">{esc(a)}<br><small>{esc(b)}</small></p>')
        else:
            body.append(f'<p>{esc(line)}</p>')
    flush_times()

    css = CSS.replace("__COL__", str(COLUMN))
    doc = ('<meta charset="utf-8">\n'
           f'<title>VALHALLA CHARITY LIVE 掲載プレビュー</title>\n'
           f'<style>{css}</style>\n'
           f'<header class="bar">'
           f'<strong>ここが正。OK が出たら CAMPFIRE へ流します</strong>'
           f'<span>図版 {n_img} 枚 ／ 動画 2 本　—　{STAMP}</span>'
           f'</header>\n'
           f'<main>\n'
           f'<p class="lead">文化 × エンタメ × AI。2026年10月18日（日）渋谷で '
           f'VALHALLA CHARITY LIVE を開催します。出演は MIO / RAY / KØU。'
           f'収益から必要経費を差し引いた全額を、公益財団法人 教育文化セキュリティ財団へお渡しします。</p>\n'
           + "\n".join(body) + "\n</main>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"{OUT}  {OUT.stat().st_size/1024/1024:.2f} MB  図版{n_img}枚")


CSS = """
:root{
  --ink:#4d4a4a; --ink-strong:#1a1416; --ground:#ffffff; --rule:#e6e2e2;
  --crimson:#c1121f; --band:#fbf4f4; --faq:#f3ecec; --chip:#d9949a;
  --black:#0a0709; --cream:#f5efe4; --muted:#8b8686;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ink:#c9c5c5; --ink-strong:#f2eeee; --ground:#141213; --rule:#332f30;
    --band:#241a1c; --faq:#211a1b; --muted:#948e8e;
  }
}
:root[data-theme="dark"]{
  --ink:#c9c5c5; --ink-strong:#f2eeee; --ground:#141213; --rule:#332f30;
  --band:#241a1c; --faq:#211a1b; --muted:#948e8e;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP",system-ui,sans-serif;
  font-size:16px;line-height:29px;-webkit-text-size-adjust:100%}
.bar{position:sticky;top:0;z-index:9;background:var(--black);color:var(--cream);
  padding:10px 18px;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap;
  border-bottom:3px solid var(--crimson);font-size:13px;line-height:1.5}
.bar strong{font-size:14px}
.bar span{color:var(--chip)}
main{max-width:__COL__px;margin:0 auto;padding:28px 16px 90px}
img{max-width:100%;height:auto;display:block}
.hero{width:100%;border-radius:2px}
.lead{font-weight:700;color:var(--ink-strong);margin:18px 0 34px}
p{margin:16px 0}
.em{font-weight:700;color:var(--ink-strong)}
.li{margin:4px 0 4px 2px;font-size:15px;line-height:26px}
.li::before{content:"・";color:var(--crimson)}
.note{font-size:13.5px;line-height:24px;color:var(--muted)}
h3{font-size:17px;line-height:27px;color:var(--ink-strong);margin:30px 0 8px}
.ch{background:var(--black);border-left:6px solid var(--crimson);
  padding:20px 22px;margin:44px 0 18px}
.eyebrow{margin:0;font-size:12px;letter-spacing:2.4px;color:var(--chip)}
.chtitle{margin:4px 0 0;font-size:24px;line-height:1.35;font-weight:700;color:var(--cream)}
.band{background:var(--band);border-left:4px solid var(--crimson);
  padding:14px 16px;margin:20px 0;font-weight:700;font-size:17px;
  line-height:32px;color:var(--ink-strong)}
blockquote{background:var(--faq);border-left:4px solid var(--crimson);
  margin:20px 0;padding:16px 18px;font-size:15px;line-height:28px}
blockquote .by{display:block;margin-top:10px;text-align:right;
  font-weight:700;color:var(--ink-strong)}
.q{background:var(--faq);border-left:4px solid var(--crimson);
  padding:12px 16px;margin:22px 0 0;font-weight:700;font-size:16px;color:var(--ink-strong)}
.a{margin:10px 0 0 4px}
.sign{margin:34px 0 10px;text-align:center;font-weight:700;font-size:20px;
  color:var(--ink-strong);letter-spacing:1px}
.sign small{display:block;margin-top:6px;font-size:14px;font-weight:400;color:var(--muted)}
.fig{margin:22px 0;position:relative}
.fig.new{outline:2px solid var(--crimson);outline-offset:3px}
.badge{position:absolute;top:8px;left:8px;background:var(--crimson);color:#fff;
  font-size:11px;letter-spacing:.06em;padding:3px 8px;border-radius:2px}
.video{display:block;position:relative;margin:22px 0;text-decoration:none;color:inherit}
.video img{width:100%}
.play{position:absolute;left:50%;top:50%;width:66px;height:46px;margin:-23px 0 0 -33px;
  background:#f00;border-radius:12px;opacity:.92}
.play::after{content:"";position:absolute;left:26px;top:13px;border-style:solid;
  border-width:10px 0 10px 17px;border-color:transparent transparent transparent #fff}
.vcap{display:block;margin-top:8px;font-size:13px;color:var(--muted)}
.tl{width:100%;border-collapse:collapse;margin:14px 0 22px;font-size:15px}
.tl th{width:104px;text-align:left;vertical-align:top;padding:8px 10px 8px 0;
  font-weight:700;color:var(--ink-strong);white-space:nowrap}
.tl td{vertical-align:top;padding:8px 0;border-bottom:1px solid var(--rule)}
.tl tr:last-child td{border-bottom:none}
@media (max-width:520px){
  .tl th{width:84px;font-size:14px} .tl td{font-size:14px}
  .chtitle{font-size:21px}
}
"""

if __name__ == "__main__":
    build()
