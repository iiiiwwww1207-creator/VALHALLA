#!/usr/bin/env python3
"""CAMPFIRE 入稿一式のフォルダを、いまのファイルから丸ごと作り直す。

これを用意した理由：一式を手でコピーして組んでいたら、直したファイルの
一部だけが差し替わって、**古いメインビジュアルの入った資料が残っていた**。
一部を更新するのではなく、毎回すべてを作り直せば、その取りこぼしは起きない。

先に図版・本文・PDF を生成し直してから、フォルダへ配る。
最後に、フォルダの中身より新しいソースが無いかを検査する。

使い方: python3 tools/build-handover.py
出力  : ~/Desktop/VALHALLA_CAMPFIRE_20260909/ と同名の .zip
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = Path.home() / "Desktop" / "VALHALLA_CAMPFIRE_20260909"
CHARITY = ROOT / "assets" / "charity"
ART = Path("/tmp/valhalla_artifact")

# 先に作り直すもの（順番に意味がある。図版 → 本文 → 各形式）
BUILDS = (
    "create_flyer_wide.py", "create_concept_banner.py", "create_axis_banner.py",
    "create_timetable_banner.py", "create_returns_banner.py",
    "create_flow_banner.py", "create_venue_banner.py",
)
TOOLS = ("build-artifact.py", "build-pdf.py", "build-body-plain.py",
         "build-body-doc.py", "build-returns-pdf.py")

# CAMPFIRE に登録する順。左が配布名、右が中身
IMAGES = (
    ("01_メインビジュアル.jpg",       CHARITY / "flyer_wide_noname.jpg"),
    ("02_出演者_MIO_RAY_KOU.jpg",     CHARITY / "group_field_panel.jpg"),
    ("03_支援コース一覧.jpg",         CHARITY / "returns_banner.jpg"),
    ("04_当日の流れ.jpg",             CHARITY / "timetable_banner.jpg"),
    ("05_会場_近日公開予定.jpg",      CHARITY / "venue_banner.jpg"),
    ("06_文化×エンタメ×AI.jpg",       CHARITY / "axis_banner.jpg"),
    ("07_支援が寄付になるまで.jpg",   CHARITY / "flow_banner.jpg"),
    ("08_前回の活動_根津神社.jpg",    CHARITY / "nezu" / "nezu_flyer_fixed.jpg"),
    ("09_3つの言葉.jpg",              CHARITY / "concept_banner.jpg"),
)
DOCS = (
    ("ページ全文（画像入り）.pdf",     ART / "campfire-draft.pdf"),
    ("ページ全文（文字化けしない版）.pdf", ART / "campfire-draft-embed.pdf"),
    ("ページ本文（貼り付け用）.txt",   ROOT / "docs" / "campfire-body-plain.txt"),
    ("ページ本文（編集用）.docx",      ROOT / "docs" / "campfire-body-edit.docx"),
    ("リターン品一覧.pdf",             ROOT / "docs" / "campfire-returns-list.pdf"),
)
FLYER = (
    ("公式フライヤー.pdf", CHARITY / "flyer_fusion_fixed.pdf"),
    ("公式フライヤー.png", CHARITY / "flyer_fusion_fixed.png"),
)


def run(cmd: list) -> None:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise RuntimeError(f"失敗: {' '.join(cmd)}")


def main() -> None:
    for name in BUILDS:
        run([sys.executable, str(CHARITY / name)])
    run([sys.executable, str(ROOT / "assets" / "charity" / "create_flyer_wide.py"),
         "--no-names"])
    for name in TOOLS:
        run([sys.executable, str(ROOT / "tools" / name)])
    run([sys.executable, str(ROOT / "tools" / "build-pdf.py"), "--embed"])

    if DEST.exists():
        shutil.rmtree(DEST)               # 残骸を残さない。毎回まっさらから
    for sub in ("画像", "フライヤー", "資料"):
        (DEST / sub).mkdir(parents=True)

    for group, folder in ((IMAGES, "画像"), (FLYER, "フライヤー"), (DOCS, "資料")):
        for name, src in group:
            if not src.exists():
                raise FileNotFoundError(f"元ファイルがありません: {src}")
            shutil.copy2(src, DEST / folder / name)

    shutil.copy2(ROOT / "docs" / "handover-readme.txt",
                 DEST / "はじめにお読みください.txt")

    # 配ったものより新しいソースが残っていないかを確かめる
    stale = [name for group, folder in ((IMAGES, "画像"), (FLYER, "フライヤー"),
                                        (DOCS, "資料"))
             for name, src in group
             if src.stat().st_mtime > (DEST / folder / name).stat().st_mtime + 1]
    if stale:
        raise RuntimeError(f"古いまま配られたファイルがあります: {stale}")

    zip_path = shutil.make_archive(str(DEST), "zip", DEST.parent, DEST.name)
    total = sum(f.stat().st_size for f in DEST.rglob("*") if f.is_file())
    print(f"{DEST}  {total/1024/1024:.1f} MB")
    print(f"{zip_path}  {Path(zip_path).stat().st_size/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
