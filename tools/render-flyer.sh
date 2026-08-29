#!/bin/sh
# VALHALLA CHARITY LIVE フライヤー 書き出しスクリプト（macOS + Google Chrome）
# 使い方:  sh render.sh
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Google Chrome が見つかりません: $CHROME"; exit 1; }
TMP=$(mktemp -d); mkdir -p export

render () { # $1=クラス $2=幅 $3=高さ $4=出力名
  python3 - "$PWD" "$1" "$TMP/$4.html" <<'PY'
import sys
base, cls, out = sys.argv[1], sys.argv[2], sys.argv[3]
h = open('src/flyer-teaser.html', encoding='utf-8').read()
h = h.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="file://%s/">' % base, 1)
h = h.replace('</style>', 'body{padding:0!important;gap:0!important;background:#000}'
              '.board{display:none!important}.board.%s{display:flex!important}\n</style>' % cls, 1)
open(out, 'w', encoding='utf-8').write(h)
PY
  "$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --virtual-time-budget=8000 --window-size="$2","$3" \
    --screenshot="$TMP/$4.png" "file://$TMP/$4.html" 2>/dev/null
  sips -z "$3" "$2" "$TMP/$4.png" --out "$TMP/$4_fit.png" >/dev/null
  sips -s format jpeg -s formatOptions 92 "$TMP/$4_fit.png" --out "export/$4.jpg" >/dev/null
  cp "$TMP/$4_fit.png" "export/$4.png"
  echo "  → export/$4.jpg"
}

echo "書き出し中..."
render t916 1080 1920 teaser_1080x1920
render t45  1080 1350 teaser_1080x1350
render t11  1080 1080 teaser_1080x1080

# 配布用PDF（A4の中央にストーリー版を収める）
cat > "$TMP/pdf.html" <<HTML
<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
@page{size:A4 portrait;margin:0}*{margin:0;padding:0}
html,body{background:#050307;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.p{width:210mm;height:297mm;display:flex;align-items:center;justify-content:center;background:#050307}
img{height:297mm;width:auto;display:block}
</style></head><body><div class="p"><img src="file://$PWD/export/teaser_1080x1920.png"></div></body></html>
HTML
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --virtual-time-budget=6000 --print-to-pdf="export/teaser_story_A4.pdf" "file://$TMP/pdf.html" 2>/dev/null
echo "  → export/teaser_story_A4.pdf"
rm -rf "$TMP"
echo "完了。export/ を確認してください。"
