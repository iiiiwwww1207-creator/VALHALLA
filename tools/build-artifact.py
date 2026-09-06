#!/usr/bin/env python3
"""CAMPFIRE 本文ドラフトを、共有できる1枚のHTMLに書き出す。

tools/build-campfire-preview.py の変換処理を再利用し、
・画像を data URI として埋め込む（外部ホストへの通信が禁止されているため）
・YouTube の埋め込みは iframe が使えないのでリンクカードに置き換える
という2点だけを変えている。

使い方: python3 tools/build-artifact.py
出力  : /tmp/valhalla_artifact/campfire-draft.html
"""
import argparse
import base64
import importlib.util
import io
import os
import re
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = Path("/tmp/valhalla_artifact/campfire-draft.html")

spec = importlib.util.spec_from_file_location("prev", HERE / "build-campfire-preview.py")
prev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prev)

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Zen+Kaku+Gothic+New:wght@400;500;700&"
         "family=Zen+Old+Mincho:wght@400;600;900&display=swap")

CSS = """
*{box-sizing:border-box}
:root{
  --paper:#FBF8F7; --card:#FFFFFF; --ink:#171216; --sub:#6B6469;
  --line:#E7DFDF; --rule:#171216;
  --crimson:#C1121F; --crimson-deep:#8E1019;
  --flag-bg:#FBF0D8; --flag-ink:#8A6410; --flag-line:#E6CE96;
  --measure:34rem;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#141013; --card:#1B1519; --ink:#F2ECEA; --sub:#A29A9E;
    --line:#2C2328; --rule:#F2ECEA;
    --crimson:#E1554F; --crimson-deep:#C1121F;
    --flag-bg:#33291A; --flag-ink:#E8C77E; --flag-line:#5A4726;
  }
}
:root[data-theme="dark"]{
  --paper:#141013; --card:#1B1519; --ink:#F2ECEA; --sub:#A29A9E;
  --line:#2C2328; --rule:#F2ECEA;
  --crimson:#E1554F; --crimson-deep:#C1121F;
  --flag-bg:#33291A; --flag-ink:#E8C77E; --flag-line:#5A4726;
}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans",system-ui,sans-serif;
  font-size:16px;line-height:2;-webkit-font-smoothing:antialiased}

.masthead{background:var(--crimson-deep);color:#FBF3F2;padding:26px 24px 22px}
.masthead .in{max-width:var(--measure);margin:0 auto}
.eyebrow{font-size:11px;letter-spacing:.22em;text-transform:uppercase;
  color:#F0B9B6;margin:0 0 10px}
.masthead h1{font-family:"Zen Old Mincho",serif;font-weight:600;
  font-size:clamp(21px,4.4vw,28px);line-height:1.45;margin:0;text-wrap:balance}
.masthead .meta{margin:14px 0 0;font-size:12.5px;color:#EBC4C1;line-height:1.9}

.stats{max-width:var(--measure);margin:0 auto;padding:0 24px;
  display:flex;gap:0;border-bottom:1px solid var(--line)}
.stat{flex:1;padding:16px 0;text-align:center}
.stat + .stat{border-left:1px solid var(--line)}
.stat b{display:block;font-family:"Zen Old Mincho",serif;font-size:24px;
  line-height:1.2;font-variant-numeric:tabular-nums}
.stat span{font-size:11px;letter-spacing:.1em;color:var(--sub)}
.stat.open b{color:var(--crimson)}

main{max-width:var(--measure);margin:0 auto;padding:8px 24px 96px}

h2{font-family:"Zen Old Mincho",serif;font-weight:600;
  font-size:20px;line-height:1.6;margin:64px 0 4px;text-wrap:balance;
  padding-bottom:14px;border-bottom:2px solid var(--rule)}
h2:first-of-type{margin-top:40px}
p{margin:0 0 18px;font-size:15.5px}
strong{font-weight:700}
ul{margin:0 0 22px;padding-left:1.25em}
li{margin-bottom:8px;font-size:15.5px}
hr{border:0;border-top:1px solid var(--line);margin:30px 0}

blockquote{margin:26px 0;padding:22px 24px;background:var(--card);
  border-left:3px solid var(--crimson);border-radius:2px}
blockquote p{margin:0 0 14px;font-family:"Zen Old Mincho",serif;font-size:15.5px}
blockquote p:last-child{margin-bottom:0}

figure{margin:28px 0}
figure img{width:100%;display:block;border-radius:2px;border:1px solid var(--line)}
figcaption{font-size:12px;color:var(--sub);margin-top:9px;text-align:center;letter-spacing:.02em}

.mv{display:block;text-decoration:none;color:inherit;background:var(--card);
  border:1px solid var(--line);border-radius:2px;padding:20px 22px;
  display:flex;gap:16px;align-items:center;transition:border-color .15s}
.mv:hover,.mv:focus-visible{border-color:var(--crimson)}
.mv .play{flex:none;width:44px;height:44px;border-radius:50%;
  background:var(--crimson);position:relative}
.mv .play::after{content:"";position:absolute;left:17px;top:13px;
  border-left:14px solid #fff;border-top:9px solid transparent;border-bottom:9px solid transparent}
.mv .t{font-weight:700;font-size:15px;line-height:1.5}
.mv .u{font-size:12px;color:var(--sub);margin-top:3px;word-break:break-all}

.tbd,.wip{color:var(--sub);border-bottom:1px dashed var(--flag-line);
  padding-bottom:1px;font-size:14.5px}

.tail{max-width:var(--measure);margin:0 auto;padding:0 24px 64px;
  font-size:12.5px;color:var(--sub);line-height:1.9}
.tail hr{margin:0 0 20px}
a{color:var(--crimson)}
:focus-visible{outline:2px solid var(--crimson);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def data_uri(path: str, maxw: int = 900, q: int = 74) -> str:
    im = Image.open(ROOT / path).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


INTERNAL = ("※", "要確定", "確認を取る", "差し替え", "§4")


def for_sharing(body: str) -> str:
    """社外に見せる版：制作側あての注記を落とし、未確定は「調整中」として示す"""
    # 内部メモは複数行にまたがることがあるので、行単位ではなく全文で消す
    body = re.sub(
        r"〔[^〕]*〕",
        lambda m: "" if any(k in m.group(0) for k in INTERNAL) else m.group(0),
        body,
        flags=re.S,
    )
    # 注記だけの行が空になるので、その行ごと落とす
    body = "\n".join(l.rstrip() for l in body.split("\n"))
    body = re.sub(r"\n[ 　]*\n[ 　]*\n+", "\n\n", body)
    return body


def wip(m) -> str:
    """残った〔…〕を調整中の印にする。具体値はそのまま見せ、空欄は『調整中』に"""
    v = m.group(1)
    if "◯" in v or v in ("本人メッセージ", "担当パート"):
        return '<span class="wip">調整中</span>'
    return f'<span class="wip">{v}</span>'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--internal", action="store_true", help="制作側あての注記も残す")
    args = ap.parse_args()

    md = open(ROOT / prev.SRC, encoding="utf-8").read()
    body = prev.extract_body(md)
    if not args.internal:
        body = for_sharing(body)
    html = prev.convert(body)
    html = re.sub(r'<span class="tbd">〔(.+?)〕</span>', wip, html)

    # 画像を埋め込む（外部ホストへは通信できないため）
    def embed(m):
        return f'<img src="{data_uri(m.group(1))}" alt="">'
    html = re.sub(r'<img src="([^"]+)" alt="">', embed, html)

    # YouTube は iframe が使えないのでリンクカードに
    def mv(m):
        vid = m.group(1)
        return (f'<a class="mv" href="https://www.youtube.com/watch?v={vid}" '
                'target="_blank" rel="noopener"><span class="play"></span>'
                '<span><span class="t">BORN IN DESPAIR -MV-【VALHALLA】</span>'
                f'<span class="u">youtube.com/watch?v={vid}</span></span></a>')
    html = re.sub(r'<div class="yt"><iframe src="https://www\.youtube\.com/embed/([\w-]+)"[^>]*></iframe></div>', mv, html)

    n_sec = html.count("<h2")
    n_img = html.count("<figure")
    n_tbd = html.count('class="wip"') + html.count('class="tbd"')

    doc = f"""<title>VALHALLA CHARITY LIVE 本文</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
<header class="masthead"><div class="in">
  <p class="eyebrow">CAMPFIRE ページ本文 ドラフト</p>
  <h1>ビジュアル系文化を守り、継ぐ。</h1>
  <p class="meta">VALHALLA CHARITY LIVE ／ 2026年10月18日（日）<br>
  CÉ LA VI TOKYO（渋谷・17F）　OPEN 19:00 ／ START 19:30 ／ 終演 21:30</p>
</div></header>
<div class="stats">
  <div class="stat"><b>{n_sec}</b><span>章</span></div>
  <div class="stat"><b>{n_img}</b><span>図版</span></div>
  <div class="stat open"><b>{n_tbd}</b><span>調整中</span></div>
</div>
<main>{html}</main>
<div class="tail"><hr>
  制作中のドラフトです。点線の箇所は現在調整中で、確定しだい差し替えます。<br>
  CAMPFIRE のページには、この文章と図版をそのまま掲載する想定です。
</div>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"{OUT}  {len(doc)/1024/1024:.2f} MB  / 章{n_sec} 図版{n_img} 未確定{n_tbd}")


if __name__ == "__main__":
    main()
