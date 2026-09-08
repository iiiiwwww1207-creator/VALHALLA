#!/usr/bin/env python3
"""CAMPFIRE 本文を、Word / Pages で直接書き直せる .docx にする。

kazuma が文言そのものを直すためのファイル。編集して送り返してもらい、
こちらで docs/campfire-project-body.md に反映する運用を想定している。

- 見出し・段落・箇条書きの構造はそのまま残す
- 画像と動画は［　］の目印だけ置く（差し込む位置が分かればよい）
- 〔　〕は黄色く塗る。**未確定なのはここ**、と一目で分かるように
- 変換は macOS の textutil を使う（pandoc も python-docx も入っていないため）

使い方: python3 tools/build-body-doc.py
出力  : docs/campfire-body-edit.docx
"""
import html
import importlib.util
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "campfire-body-edit.docx"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"build-{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prev = _load("campfire-preview")
art = _load("artifact")

CSS = """
body{font-family:'Hiragino Sans','Yu Gothic',sans-serif;font-size:11pt;line-height:1.9}
h1{font-size:16pt;border-bottom:2px solid #C1121F;padding-bottom:6pt}
h2{font-size:13pt;color:#8E1019;margin-top:22pt;border-bottom:1px solid #ddd;padding-bottom:3pt}
p{margin:0 0 9pt}
li{margin:0 0 4pt}
.asset{color:#777;font-size:9.5pt}
.tbd{background:#FFF3B0}
.note{color:#777;font-size:9.5pt;border-left:3px solid #ddd;padding-left:8pt}
blockquote{border-left:3px solid #C1121F;padding-left:10pt;margin:0 0 9pt;color:#444}
hr{border:none;border-top:1px solid #ddd;margin:14pt 0}
"""


def esc(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"〔(.*?)〕", r'<span class="tbd">〔\1〕</span>', t)
    return t


def to_html(body: str) -> str:
    out, ul, para, quote, bq = [], False, [], [], False

    def flush_para():
        if para:
            out.append(f"<p>{esc(''.join(para))}</p>")
            para.clear()

    def close_ul():
        nonlocal ul
        flush_para()
        if ul:
            out.append("</ul>")
            ul = False

    def flush_quote():
        if quote:
            out.append(f"<p>{esc(''.join(quote))}</p>")
            quote.clear()

    for raw in body.split("\n"):
        s = raw.strip()
        if bq and not (s.startswith("> ") or s == ">"):
            flush_quote()
            out.append("</blockquote>")
            bq = False
        if not s:
            close_ul()
            continue

        m = re.match(r"^【動画】(\S+)\s*(?:…\s*(.*))?$", s)
        if m:
            close_ul()
            cap = f"　{m.group(2)}" if m.group(2) else ""
            out.append(f'<p class="asset">［動画：{html.escape(m.group(1))}{html.escape(cap)}］</p>')
            continue

        m = re.match(r"^【画像】(.*?)`([^`]+)`(.*)$", s)
        if m:
            close_ul()
            cap = (m.group(1).strip() + " " + m.group(3).strip()).strip()
            cap = re.sub(r"^[（(]|[）)]$", "", cap)
            name = Path(m.group(2)).name
            out.append(f'<p class="asset">［画像：{html.escape(name)}'
                       f'{"　" + html.escape(cap) if cap else ""}］</p>')
            continue

        if s.startswith("### "):
            close_ul()
            out.append(f"<h2>{esc(s[4:])}</h2>")
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
            quote.append(t) if t else flush_quote()
            continue

        if s.startswith("- ") or s.startswith("・"):
            if not ul:
                flush_para()
                out.append("<ul>")
                ul = True
            out.append(f"<li>{esc(s[2:] if s.startswith('- ') else s[1:])}</li>")
            continue

        if ul:
            out.append("</ul>")
            ul = False
        para.append(s)

    flush_quote()
    close_ul()
    if bq:
        out.append("</blockquote>")
    return "\n".join(out)


def main() -> None:
    md = (ROOT / prev.SRC).read_text(encoding="utf-8")
    body = art.for_sharing(prev.extract_body(md))
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>VALHALLA CHARITY LIVE ／ CAMPFIRE 本文</title><style>{CSS}</style></head><body>
<h1>VALHALLA CHARITY LIVE ／ CAMPFIRE 本文</h1>
<p class="note">このファイルは文言を直すためのものです。上書きして送り返してください。<br>
黄色く塗ってあるところ〔　〕が未確定です。［画像：〜］［動画：〜］は差し込む位置の目印で、
実物はこちらで入れます。</p>
{to_html(body)}
</body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "body.html"
        src.write_text(doc, encoding="utf-8")
        subprocess.run(
            ["textutil", "-convert", "docx", "-output", str(OUT), str(src)],
            check=True, capture_output=True,
        )
    print(f"{OUT}　{OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
