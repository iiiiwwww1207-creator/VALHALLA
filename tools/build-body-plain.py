#!/usr/bin/env python3
"""CAMPFIRE に貼る本文だけを、通しで読めるテキストにまとめる。

原稿（docs/campfire-project-body.md）には制作側あての注記が大量に混ざっている。
ここでは §3 本文だけを取り出し、内部メモを落として、通読・校正できる形にする。

- 見出しは「1. 〜」のまま、前後に区切りを入れて読みやすくする
- 強調の ** は外す（読みづらいだけで、CAMPFIRE の編集画面では手で付け直す）
- 【画像】/【動画】は［　］で、何をどこに入れるかが分かる形に置き換える
- 〔　〕は未確定のまま残す。**これが残っている箇所は公開前に埋める**

使い方: python3 tools/build-body-plain.py
出力  : docs/campfire-body-plain.txt
"""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "campfire-body-plain.txt"

spec = importlib.util.spec_from_file_location(
    "prev", ROOT / "tools" / "build-campfire-preview.py"
)
prev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prev)

art_spec = importlib.util.spec_from_file_location(
    "art", ROOT / "tools" / "build-artifact.py"
)
art = importlib.util.module_from_spec(art_spec)
art_spec.loader.exec_module(art)

RULE = "─" * 46


def plain(body: str) -> str:
    out, tbd = [], 0
    for raw in body.split("\n"):
        line = raw.rstrip()

        m = re.match(r"^### (.+)$", line)
        if m:
            out += ["", RULE, m.group(1), RULE, ""]
            continue

        m = re.match(r"^【画像】(?:([^`]*))?`(.+?)`(?:（(.+?)）)?\s*$", line)
        if m:
            caption = (m.group(1) or m.group(3) or "").strip()
            name = Path(m.group(2)).name
            out.append(f"［画像：{name}{'　' + caption if caption else ''}］")
            continue

        m = re.match(r"^【動画】(\S+)\s*(?:…\s*(.*))?$", line)
        if m:
            out.append(f"［動画：{m.group(1)}{'　' + m.group(2) if m.group(2) else ''}］")
            continue

        if line.startswith("> "):
            line = "  " + line[2:]
        elif line == ">":
            line = ""

        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = line.replace("──────────────", "  - - - - -")
        tbd += len(re.findall(r"〔[^〕]*〕", line))
        out.append(line)

    text = "\n".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n", tbd


def main() -> None:
    md = (ROOT / prev.SRC).read_text(encoding="utf-8")
    body = art.for_sharing(prev.extract_body(md))
    text, tbd = plain(body)
    header = (
        "VALHALLA CHARITY LIVE ／ CAMPFIRE 本文（通し版）\n"
        "2026年10月18日（日）渋谷　OPEN 19:00 ／ START 19:25 ／ 終演 21:10\n"
        f"※ 〔　〕は未確定：残り {tbd} 箇所\n\n"
    )
    OUT.write_text(header + text, encoding="utf-8")
    print(f"{OUT}　{len(text)}字 / 未確定 {tbd}箇所")


if __name__ == "__main__":
    main()
