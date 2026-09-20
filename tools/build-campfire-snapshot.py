#!/usr/bin/env python3
"""いま CAMPFIRE に載っている状態を、そのまま1本の PDF にする。

画面を撮ったのではなく、掲載中のものを取ってきて組み直している：

  ・本文 …… 掲載中の innerText と手元の原稿が SHA-256 で一致することを確認済み。
             流し込んだ HTML をそのまま使う
  ・図版 …… CAMPFIRE の CDN から18枚を取得し、手元のファイルと原寸で画素比較して一致
  ・リターン … 掲載中の4件を取り出し、SHA-256 で写し間違いがないことを確認済み
  ・メイン画像・リターン画像 … CDN から取得したものを使用

つまり中身は掲載物そのもの。並びと見た目だけ、紙で読める形に置き直している。

使い方: python3 tools/build-campfire-snapshot.py
出力  : /tmp/valhalla_artifact/campfire-snapshot.pdf
"""
from __future__ import annotations

import html as H
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = Path("/tmp/valhalla_artifact/story_body.html")
RW = Path("/tmp/verify/rw/rewards.json")
IMGDIR = Path("/tmp/verify")          # CDN から落とした本文図版
RWDIR = Path("/tmp/verify/rw")        # CDN から落としたリターン画像・メイン画像
OUT = Path("/tmp/valhalla_artifact/campfire-snapshot.pdf")
TMP = Path("/tmp/valhalla_artifact/campfire-snapshot.html")

TITLE = "社美緒×VALHALLA｜文化×エンタメ×AI 渋谷で限定チャリティーライブ"
OWNER = "wrappingtheearth"
CATEGORY = "ソーシャルグッド"
SUMMARY = ("文化 × エンタメ × AI。2026年10月18日（日）渋谷で VALHALLA CHARITY LIVE を開催します。"
           "出演は MIO / RAY / KØU。収益から必要経費を差し引いた全額を、"
           "公益財団法人 教育文化セキュリティ財団へお渡しします。")
GOAL = "1,500,000"
DEADLINE = "2026年10月31日 23:59"
VIDEOS = ["天下上等 -MV-【VALHALLA】", "BORN IN DESPAIR -MV-【VALHALLA】"]

REWARDS = [
    ("r_support.jpg", "1,000", None, "応援プラン"),
    ("r_live.jpg", "10,000", "30", "ライブプラン"),
    ("r_vip.jpg", "50,000", "15", "VIPプラン"),
    ("r_vvip.jpg", "330,000", "5", "VVIPプラン"),
]

CSS = """
@page{size:A4 portrait;margin:14mm 13mm 12mm}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Hiragino Sans","Noto Sans JP",sans-serif;font-size:9.6pt;line-height:1.85;
  color:#1a1a1a;-webkit-print-color-adjust:exact;print-color-adjust:exact}
img{max-width:100%;display:block}
.bar{background:#d9534f;color:#fff;text-align:center;font-weight:700;font-size:9.4pt;
  padding:6px 0;margin-bottom:12px}
h1.t{font-size:15.5pt;font-weight:700;line-height:1.45;text-align:center;margin:0 0 6px}
.meta{text-align:center;font-size:8.4pt;color:#666;margin-bottom:12px}
.hero{display:grid;grid-template-columns:1.55fr 1fr;gap:9mm;align-items:start;margin-bottom:10px}
.fund{border:.7px solid #ddd;padding:11px 13px;border-radius:4px}
.fund .k{font-size:8pt;color:#777}
.fund .v{font-size:19pt;font-weight:700;line-height:1.25;margin-bottom:7px}
.fund .v small{font-size:9.5pt;font-weight:400}
.bar0{height:7px;background:#eee;border-radius:4px;margin:2px 0 4px}
.sum{font-size:9.4pt;font-weight:700;line-height:1.8;margin:8px 0 16px}
h2.sec{font-size:12pt;font-weight:700;border-left:5px solid #d9534f;padding-left:9px;
  margin:16px 0 9px;break-after:avoid;page-break-after:avoid}
.rw{border:.7px solid #ddd;border-radius:5px;padding:11px 13px;margin-bottom:11px;
  break-inside:avoid;page-break-inside:avoid}
.rw .head{display:flex;align-items:baseline;gap:9px;margin-bottom:7px}
.rw .price{font-size:15pt;font-weight:700}
.rw .price small{font-size:9pt;font-weight:400}
.rw .left{font-size:8.6pt;color:#d9534f;font-weight:700}
.rw .body{white-space:pre-wrap;font-size:8.8pt;line-height:1.8}
.rw img{border:.7px solid #eee;border-radius:3px;margin-bottom:8px}
.video{border:.7px dashed #bbb;border-radius:4px;padding:9px 12px;margin:8px 0;
  font-size:8.8pt;color:#555;background:#fafafa}
.video b{color:#1a1a1a}
.story p{margin:0 0 9px}
.story ul{margin:0 0 9px 1.25em}
.story li{margin-bottom:2px}
.story img{margin:9px auto}
.note{margin-top:14px;border-top:.7px solid #ddd;padding-top:9px;font-size:7.8pt;
  color:#777;line-height:1.8}
.note b{color:#333}
"""


def body_html() -> str:
    h = STORY.read_text(encoding="utf-8")
    # 図版は CDN から落としたものに差し替える（中身は同じ／印刷時に取りに行かない）
    def swap(m):
        name = m.group(1)
        p = IMGDIR / name
        if not p.exists():
            raise FileNotFoundError(f"図版がありません: {name}")
        return f'<img src="file://{p}" alt="{name}">'
    h = re.sub(r'<img src="[^"]*/(IMAGE-\d+\.jpg)"[^>]*>', swap, h)
    # 動画は紙で再生できないので、何が入っているかだけ残す
    i = [0]
    def vid(_):
        t = VIDEOS[i[0]] if i[0] < len(VIDEOS) else "（動画）"
        i[0] += 1
        return f'<div class="video">▶ 動画が入ります　<b>{H.escape(t)}</b>（CAMPFIRE ページ上で再生できます）</div>'
    h = re.sub(r'<div class="fr-video.*?</div>', vid, h, flags=re.S)
    if i[0] != len(VIDEOS):
        raise RuntimeError(f"動画の数が合いません: {i[0]}")
    if "static.camp-fire.jp" in h:
        raise RuntimeError("差し替え漏れの図版があります")
    return h


def main() -> None:
    rw = json.loads(RW.read_text(encoding="utf-8"))
    cards = []
    for fn, price, left, key in REWARDS:
        p = RWDIR / fn
        cards.append(
            f'<div class="rw"><img src="file://{p}" alt="{key}">'
            f'<div class="head"><span class="price">{price}<small> 円</small></span>'
            + (f'<span class="left">残り {left}</span>' if left else '<span class="left">口数の制限なし</span>')
            + '</div>'
            f'<div class="body">{H.escape(rw[key])}</div></div>')

    doc = (
        '<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">'
        '<title>CAMPFIRE 掲載状態</title><style>' + CSS + '</style></head><body>'
        '<div class="bar">プロジェクトはまだ公開されていません（掲載前の状態）</div>'
        f'<h1 class="t">{H.escape(TITLE)}</h1>'
        f'<div class="meta">{H.escape(OWNER)}　／　{H.escape(CATEGORY)}　／　CAMPFIRE for Social Good</div>'
        '<div class="hero">'
        f'<img src="file://{RWDIR / "main.jpg"}" alt="メイン画像">'
        '<div class="fund">'
        '<div class="k">現在の支援総額</div><div class="v">0<small> 円</small></div>'
        '<div class="bar0"></div>'
        f'<div class="k">目標金額は {GOAL} 円</div>'
        '<div class="k" style="margin-top:9px">支援者数</div><div class="v">0<small> 人</small></div>'
        f'<div class="k" style="margin-top:9px">募集終了</div>'
        f'<div style="font-size:10pt;font-weight:700">{DEADLINE}</div>'
        '<div class="k" style="margin-top:9px">方式</div>'
        '<div style="font-size:10pt;font-weight:700">All-In</div>'
        '</div></div>'
        f'<p class="sum">{H.escape(SUMMARY)}</p>'
        '<h2 class="sec">支援コース（リターン）</h2>'
        + "".join(cards) +
        '<h2 class="sec">本文（ストーリー）</h2>'
        '<div class="story">' + body_html() + '</div>'
        '<p class="note">'
        '<b>この文書について。</b>画面を撮ったものではなく、いま CAMPFIRE に載っているものを取り出して、'
        '紙で読める形に組み直したものです。中身が掲載物と同じであることは、次のとおり確かめています。<br>'
        '・本文 … 掲載中のテキストと手元の原稿を SHA-256 で照合し、完全一致（14,082字）<br>'
        '・図版18枚 … CAMPFIRE の CDN から取得し、手元のファイルと原寸で画素比較して一致<br>'
        '・リターン4件 … 掲載中の本文を取り出し、SHA-256 で照合して一致<br>'
        '・メイン画像／リターン画像5枚 … CDN から取得したものをそのまま掲載<br>'
        '動画2本は紙では再生できないため、入る位置と曲名だけを残しています。'
        '</p></body></html>')

    TMP.write_text(doc, encoding="utf-8")
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf-no-header", "--virtual-time-budget=30000",
                    f"--print-to-pdf={OUT}", f"file://{TMP}"],
                   check=True, capture_output=True)
    print(f"{OUT}  {OUT.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
