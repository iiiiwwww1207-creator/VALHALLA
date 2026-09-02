#!/bin/sh
# 静的LPのプレビュー用に、必要なファイルだけ /tmp/valhalla_preview へ配置する。
#
# なぜ /tmp か:
#   Claude Code のプレビュープロセスはサンドボックス下で動き、
#   Desktop 配下（このリポジトリ）を読めず、os.getcwd() も PermissionError になる。
#   そのため配信対象を /tmp に置き、serve.py に絶対パスで渡す必要がある。
#   /tmp は再起動で消えるので、消えたらこのスクリプトを流し直す。
#
# 使い方:
#   sh tools/preview-sync.sh   # 同期
#   そのあと preview_start で launch.json の "charity" を起動する（:8090）
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PREV=/tmp/valhalla_preview

mkdir -p "$PREV/assets" "$PREV/images"
cp "$ROOT/tools/serve.py" "$PREV/serve.py"

for f in charity.html campfire-preview.html lp.html index.html teaser.html proposal.html lp.css style.css navi.css; do
  [ -f "$ROOT/$f" ] && cp "$ROOT/$f" "$PREV/$f"
done

cp -R "$ROOT/assets/charity" "$PREV/assets/"
cp -R "$ROOT/images/cast" "$PREV/images/"

echo "synced -> $PREV"
