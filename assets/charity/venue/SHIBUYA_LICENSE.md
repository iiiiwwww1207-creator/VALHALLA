# 渋谷夜景写真のライセンス

いずれも **Unsplash License**。商用利用可・改変可・帰属表示は不要（クレジット記載は推奨）。
取得日 2026-09-07。

| ファイル | 出典 | 寸法 |
|---|---|---|
| `shibuya_free_a.jpg` | https://unsplash.com/photos/busy-city-intersection-at-night-with-bright-neon-signs-t1WmHgOynnU | 3000x4500 |
| `shibuya_free_b.jpg` | https://unsplash.com/photos/busy-shibuya-crossing-at-night-with-neon-lights-fzFLX8gk3eE | 3000x4500 |

## ⚠️ 削除した写真（使用不可）
kazuma が LINE で送った出所不明の空撮写真（710x1066・Exif が空・明らかにプロの作例）を
一度 `shibuya_src.jpg` / `shibuya_night.jpg` として取り込んだが、
**権利が確認できないため作業ツリーから削除した。**

**🔴 このリポジトリは PUBLIC。** 一度 push した（コミット 7f88162）ため、
**削除後も git の履歴には残り、GitHub 上から辿れる。**
完全に消すには履歴の書き換え（`git filter-repo` 等）と force push が必要で、
これは破壊的操作なので **kazuma の判断を仰ぐこと。**


## 削除した店舗写真（2026-09-07）
`deploy-app.yml` は **`assets/charity` を丸ごと Pages にコピーする**ため、
HTML から参照していなくても**公開 URL でアクセスできてしまう**。
実際 `club.jpg` `dj.jpg` `stage.jpg` `roof.jpg` `roofnight.jpg` `celavi_red.jpg`
`floor.jpg` は main に入っており**すでに配信されていた**。

会場の許可が取れていない以上これらを配信し続けるべきではないため、
**リポジトリから削除した**（kazuma の手元に原本がある）。
`laser_band_a.jpg`（同じ写真の天井部分の切り出し）と、その生成に使う
`make_laser_band.py` / `upscale_celavi_red.py` も同時に削除した。

⚠️ **git の履歴には残る。** このリポジトリは PUBLIC なので、
過去のコミットを辿れば取得できる。完全に消すには履歴の書き換えと
force push が必要で、破壊的操作のため kazuma の判断待ち。
