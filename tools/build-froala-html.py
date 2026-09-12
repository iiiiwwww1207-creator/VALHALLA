#!/usr/bin/env python3
"""CAMPFIRE のストーリー欄（Froala エディタ）に流し込む HTML を書き出す。

エディタは見出し・太字・箇条書き・引用しか持たないので、装飾は付けない。
画像は、あとから手で入れる位置が分かるように**目印の段落**を残す。
目印は差し込んだら消す。消し忘れても本番で目立つように大文字で書く。

使い方: python3 tools/build-froala-html.py
出力  : /tmp/valhalla_artifact/story.html （貼り込み用）
        /tmp/valhalla_artifact/story_images.txt （画像の順番）
"""
import html
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("/tmp/valhalla_artifact/story.html")
LIST = Path("/tmp/valhalla_artifact/story_images.txt")


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / fn)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prev = load("prev", "build-campfire-preview.py")
art = load("art", "build-artifact.py")


def inline(t: str) -> str:
    t = html.escape(t)
    # 強調は行をまたぐことがあるので改行も拾う
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t, flags=re.S)
    t = re.sub(r"`(.+?)`", r"\1", t)
    return t


def convert(body: str):
    out, images = [], []
    para, quote, items = [], [], []

    # 強調が2行にまたがることがあるので、行ごとではなく段落をまとめて変換する
    def block(lines):
        return inline("\n".join(lines)).replace("\n", "<br>")

    def flush_para():
        if para:
            out.append("<p>" + block(para) + "</p>")
            para.clear()

    def flush_quote():
        if quote:
            out.append("<blockquote><p>" + block(quote) + "</p></blockquote>")
            quote.clear()

    def flush_items():
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    def flush_all():
        flush_para(); flush_quote(); flush_items()

    for raw in body.split("\n"):
        line = raw.rstrip()

        m = re.match(r"^### (.+)$", line)
        if m:
            flush_all()
            out.append(f"<h2>{inline(m.group(1))}</h2>")
            continue

        m = re.match(r"^【画像】(?:([^`]*))?`(.+?)`(?:（(.+?)）)?\s*$", line)
        if m:
            flush_all()
            n = len(images) + 1
            name = Path(m.group(2)).name
            cap = (m.group(1) or m.group(3) or "").strip()
            images.append((n, m.group(2), cap))
            out.append(f'<p>▼ IMAGE-{n:02d} ここに画像 {name}'
                       + (f'（{html.escape(cap)}）' if cap else '') + "</p>")
            continue

        m = re.match(r"^【動画】(\S+)\s*(?:…\s*(.*))?$", line)
        if m:
            flush_all()
            out.append(f'<p><a href="{m.group(1)}">{m.group(1)}</a>'
                       + (f"　{inline(m.group(2))}" if m.group(2) else "") + "</p>")
            continue

        if line.startswith("- "):
            flush_para(); flush_quote()
            items.append(inline(line[2:]))
            continue
        if line.startswith("> "):
            flush_para(); flush_items()
            quote.append(line[2:])
            continue
        if line == ">":                     # 引用の中の空行。引用を切らない
            if quote:
                quote.append("")
            continue
        if line.startswith("─" * 6):
            flush_all()
            out.append("<hr>")
            continue
        if not line:
            flush_all()
            continue
        flush_quote(); flush_items()
        para.append(line)

    flush_all()
    return "\n".join(out), images


def main() -> None:
    md = (ROOT / prev.SRC).read_text(encoding="utf-8")
    body = art.for_sharing(prev.extract_body(md))
    doc, images = convert(body)
    OUT.write_text(doc, encoding="utf-8")
    LIST.write_text("\n".join(f"IMAGE-{n:02d}\t{p}\t{c}" for n, p, c in images),
                    encoding="utf-8")
    print(f"{OUT}  {len(doc):,} 文字  画像 {len(images)} 点")
    for n, p, c in images:
        print(f"  IMAGE-{n:02d}  {p}")


if __name__ == "__main__":
    main()
