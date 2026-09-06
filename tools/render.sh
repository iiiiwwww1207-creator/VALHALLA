#!/bin/bash
# フライヤー書き出し（macOS + Google Chrome）
#   使い方: sh tools/render.sh <html> <出力名> [幅 高さ]
#     A4:      sh tools/render.sh flyer-fusion.html flyer_fusion
#     ボード:  sh tools/render.sh flyer-teaser.html teaser_1080x1920 t916 1080 1920
set -e
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="$1"; OUT="$2"; CLS="$3"; W="${4:-794}"; H="${5:-1123}"
TMP=$(mktemp -d); mkdir -p dist
python3 - "$PWD" "$SRC" "$CLS" "$TMP/p.html" <<'PY'
import sys
base, src, cls, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
h = open(src, encoding='utf-8').read()
h = h.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<base href="file://%s/">' % base, 1)
extra = 'body{padding:0!important;gap:0!important;background:#000}.page{box-shadow:none!important}'
if cls:
    extra += '.board{display:none!important}.board.%s{display:flex!important}' % cls
h = h.replace('</style>', extra + '\n</style>', 1)
open(out, 'w', encoding='utf-8').write(h)
PY
"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=3 \
  --virtual-time-budget=8000 --window-size="$W","$H" \
  --screenshot="$TMP/o.png" "file://$TMP/p.html" 2>/dev/null
if [ -n "$CLS" ]; then sips -z "$H" "$W" "$TMP/o.png" --out "dist/$OUT.png" >/dev/null
else cp "$TMP/o.png" "dist/$OUT.png"; fi
sips -Z 1588 -s format jpeg -s formatOptions 90 "dist/$OUT.png" --out "dist/$OUT.jpg" >/dev/null
if [ -z "$CLS" ]; then
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
    --virtual-time-budget=8000 --print-to-pdf="dist/$OUT.pdf" "file://$PWD/$SRC" 2>/dev/null
fi
rm -rf "$TMP"; echo "→ dist/$OUT"
