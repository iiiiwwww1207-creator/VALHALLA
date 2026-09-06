#!/usr/bin/env python3
"""docs/campfire-project-body.md の「§3 本文」だけを取り出して、
CAMPFIRE のプロジェクトページに近い見た目の HTML を書き出す。

CAMPFIRE 本文は白地・本文幅700px前後・表なしなので、それに寄せている。
実際に貼ったときの見え方と、画像の入る位置を確認するためのもの。

使い方: python3 tools/build-campfire-preview.py
出力  : campfire-preview.html
"""
import html
import os
import re

SRC = "docs/campfire-project-body.md"
OUT = "campfire-preview.html"


def extract_body(md: str) -> str:
    m = re.search(r"^## §3 本文.*?$(.*?)^---\s*$", md, re.M | re.S)
    if not m:
        raise SystemExit("§3 本文が見つからない")
    body = m.group(1)
    body = body.split("（本文ここまで）")[0]
    return body.strip()


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def convert(body: str) -> str:
    out, ul, para = [], False, []
    bq, quote = False, []
    hn = [0]

    def flush_quote():
        if quote:
            out.append("<p>" + inline("".join(quote)) + "</p>")
            quote.clear()

    def flush_para():
        if para:
            t = inline("".join(para))
            t = re.sub(r"〔(.+?)〕", r'<span class="tbd">〔\1〕</span>', t)
            out.append(f"<p>{t}</p>")
            para.clear()

    def close_ul():
        nonlocal ul
        flush_para()
        if ul:
            out.append("</ul>")
            ul = False

    for raw in body.split("\n"):
        line = raw.rstrip()
        s = line.strip()

        if not s:
            close_ul()
            continue

        if s.startswith("【動画】"):
            close_ul()
            out.append(
                '<figure class="video"><div class="ph">'
                + inline(s[4:]) + "</div></figure>"
            )
            continue

        m = re.match(r"^【画像】(.*?)`([^`]+)`(.*)$", s)
        if m:
            close_ul()
            src = m.group(2)
            cap = (m.group(1).strip() + " " + m.group(3).strip()).strip()
            exists = os.path.exists(src)
            cap = re.sub(r"^[（(]|[）)]$", "", cap)
            out.append('<figure class="img%s">' % ("" if exists else " missing"))
            if exists:
                out.append(f'<img src="{html.escape(src)}" alt="">')
            else:
                out.append(f'<div class="ph">画像が見つかりません: {html.escape(src)}</div>')
            if cap:
                out.append(f"<figcaption>{inline(cap)}</figcaption>")
            out.append("</figure>")
            continue

        if s.startswith("### "):
            close_ul()
            hn[0] += 1
            out.append(f'<h2 id="s{hn[0]}">{inline(s[4:])}</h2>')
            continue

        if set(s) <= {"─"} and len(s) > 3:
            close_ul()
            out.append("<hr>")
            continue

        if s.startswith("> ") or s == ">":
            if not bq:
                close_ul()
                out.append("<blockquote>")
                bq = True
            t = s[2:].strip()
            if t:
                quote.append(t)
            else:
                flush_quote()
            continue
        if bq:
            flush_quote()
            out.append("</blockquote>")
            bq = False

        if s.startswith("- ") or s.startswith("・"):
            if not ul:
                out.append("<ul>")
                ul = True
            out.append(f"<li>{inline(s[2:] if s.startswith('- ') else s[1:])}</li>")
            continue

        # 段落は空行まで継続する。ここでリストだけ閉じ、para はフラッシュしない
        if ul:
            out.append("</ul>")
            ul = False
        # 原稿の折り返しは段落の切れ目ではないので、空行までを1段落にまとめる
        para.append(s)

    flush_para()
    close_ul()
    if bq:
        flush_quote()
        out.append("</blockquote>")
    return "\n".join(out)


CSS = """
:root{--ink:#1a1a1a;--sub:#666;--line:#e3e3e3;--accent:#1f9e8e}
*{box-sizing:border-box}
body{margin:0;background:#f5f5f5;color:var(--ink);
  font-family:"Hiragino Sans","Noto Sans JP",system-ui,sans-serif;line-height:1.9}
.note{max-width:760px;margin:0 auto;padding:14px 24px;background:#fffbe6;
  border-bottom:1px solid #f0e0a0;font-size:13px;color:#7a6a20}
main{max-width:760px;margin:0 auto;background:#fff;padding:44px 30px 80px;
  border-left:1px solid var(--line);border-right:1px solid var(--line);min-height:100vh}
h2{font-size:21px;font-weight:700;margin:52px 0 18px;padding-bottom:10px;
  border-bottom:2px solid var(--ink);letter-spacing:.02em}
h2:first-of-type{margin-top:0}
p{margin:0 0 16px;font-size:15.5px}
ul{margin:0 0 20px;padding-left:1.3em}
li{margin-bottom:7px;font-size:15.5px}
strong{font-weight:700}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
figure.img{margin:26px 0}
figure.img img{width:100%;display:block;border-radius:3px}
figcaption{font-size:12.5px;color:var(--sub);margin-top:8px;text-align:center}
.ph{padding:36px;border:2px dashed #d33;color:#d33;text-align:center;font-size:13px;border-radius:4px}
blockquote{margin:22px 0;padding:18px 22px;border-left:4px solid var(--ink);background:#fafafa}
blockquote p{margin:0 0 12px;font-size:15.5px}
blockquote p:last-child{margin-bottom:0}
figure.video{margin:26px 0}
figure.video .ph{border-color:#1f9e8e;color:#1a7a6e;background:#f2fbfa}
.tbd{background:#ffe9a8;color:#8a6b00;padding:1px 5px;border-radius:3px;font-weight:700}
code{background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:13px}
"""


def main() -> None:
    md = open(SRC, encoding="utf-8").read()
    body = convert(extract_body(md))
    n_img = body.count("<figure")
    n_missing = body.count("missing")
    n_tbd = body.count('class="tbd"')
    note = (
        f"CAMPFIRE 本文プレビュー ／ 画像 {n_img} 枚"
        + (f"（うち読み込めないもの {n_missing} 枚）" if n_missing else "")
        + f" ／ 未確定の箇所 <b>{n_tbd}</b> 件（黄色のハイライト）"
        + " ／ 出典: docs/campfire-project-body.md の §3 本文"
    )
    doc = (
        "<!doctype html><html lang='ja'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>CAMPFIRE 本文プレビュー ｜ VALHALLA CHARITY LIVE</title>"
        f"<style>{CSS}</style></head><body>"
        f"<div class='note'>{note}</div><main>{body}</main></body></html>"
    )
    open(OUT, "w", encoding="utf-8").write(doc)
    print(f"{OUT} ({len(doc)} bytes) / images={n_img} missing={n_missing} tbd={n_tbd}")


if __name__ == "__main__":
    main()
