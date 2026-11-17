#!/usr/bin/env python3
"""朝日奈優が出ている YouTube の回を、公式 API（YouTube Data API v3）で洗い出す。

各チャンネルの全動画のタイトル・概要欄を読み、名前などが入っている回を一覧にする。
名前がどこにも書かれていない「映っているだけの回」は見つけられない。

API キーはチャットやリポジトリに置かない。kazuma が自分で次のファイルに入れる:
    ~/.config/valhalla/youtube_api_key   （中身はキーの1行だけ・権限 600）
環境変数 YT_API_KEY があればそちらを優先する。キーの中身は表示しない。

使い方:
    python3 tools/find_yu_videos.py            # 結果を表で表示
    python3 tools/find_yu_videos.py --json out.json
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

KEY_FILE = Path.home() / ".config" / "valhalla" / "youtube_api_key"
API = "https://www.googleapis.com/youtube/v3/"

# 調べるチャンネル（ID が分かっているものは ID、分からないものはハンドル）
CHANNELS = [
    {"name": "Mio Yashiro TV -ANOTHER STORY-", "handle": "@MioYashiroTV-ANOTHERSTORY-"},
    {"name": "Mio Yashiro TV", "handle": "@MioYashiroTV"},
    {"name": "階段降りたらVALHALLA", "id": "UCBTAJ9FuUNMHa1o3JtLt4oA"},
    {"name": "ゆっきーTV -桜威優希斗-", "id": "UCTNUTlMgMT2fIRBruz-etQw"},
]

# 本人だと言える手がかり（強い）と、本人の可能性がある手がかり（弱い）
STRONG = re.compile(r"朝日奈|あさひなゆう|valhalla_yuu|ばじひな|バジひな")
WEAK = re.compile(r"場地")


def load_key():
    key = os.environ.get("YT_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
    if not key:
        sys.exit(f"API キーが見つからない。{KEY_FILE} にキーを1行で入れてから、もう一度動かして。")
    return key


def get(endpoint, key, **params):
    params["key"] = key
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # キーを含む URL は出さない
        body = e.read().decode("utf-8", "replace")
        reason = re.search(r'"reason":\s*"([^"]+)"', body)
        sys.exit(f"YouTube API がエラーを返した（{e.code} {reason.group(1) if reason else ''}）: {endpoint}")


def uploads_playlist(ch, key):
    params = {"part": "contentDetails"}
    if "id" in ch:
        params["id"] = ch["id"]
    else:
        params["forHandle"] = ch["handle"]
    items = get("channels", key, **params).get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def all_videos(playlist, key):
    token = None
    while True:
        params = {"part": "snippet", "playlistId": playlist, "maxResults": 50}
        if token:
            params["pageToken"] = token
        data = get("playlistItems", key, **params)
        for it in data.get("items", []):
            sn = it["snippet"]
            yield {
                "id": sn["resourceId"]["videoId"],
                "title": sn["title"],
                "description": sn.get("description", ""),
                "published": sn.get("publishedAt", "")[:10],
            }
        token = data.get("nextPageToken")
        if not token:
            return


def main():
    key = load_key()
    found, summary = [], []
    for ch in CHANNELS:
        pl = uploads_playlist(ch, key)
        if not pl:
            summary.append(f"{ch['name']}: チャンネルが見つからなかった")
            continue
        n = 0
        for v in all_videos(pl, key):
            n += 1
            text = v["title"] + "\n" + v["description"]
            if STRONG.search(text):
                level = "確定"
            elif WEAK.search(text):
                level = "要確認"
            else:
                continue
            hit = (STRONG.search(text) or WEAK.search(text)).group(0)
            where = "タイトル" if re.search(re.escape(hit), v["title"]) else "概要欄"
            found.append({"channel": ch["name"], "level": level, "hit": f"{where}に「{hit}」",
                          "id": v["id"], "published": v["published"], "title": v["title"]})
        summary.append(f"{ch['name']}: {n}本を確認")

    found.sort(key=lambda x: (x["channel"], x["published"]), reverse=True)
    print("\n".join(summary))
    print()
    for f in found:
        print(f"[{f['level']}] {f['published']} {f['channel']} | {f['id']} | {f['hit']} | {f['title']}")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        Path(out).write_text(json.dumps(found, ensure_ascii=False, indent=2))
        print(f"\n{out} に保存した")


if __name__ == "__main__":
    main()
