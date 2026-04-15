## Project: ヴァルハラ × ユグドラ デモ版 Phase 1

### 概要
- **目的**: 4/18 MTGで見せるデモ画面を最速で作る
- **スコープ**: ヴァルハラ（診断+結果）+ ユグドラ（診断+タロット占い）
- **実装分担**: Codex → ヴァルハラ / Gemini → ユグドラ / Claude → レビュー・統合

---

## Phase 0: 作業準備

- [x] [id:setup] [required] monorepo骨格作成（pnpm + turborepo）
- [x] [id:shared] [required] 共通パッケージ作成（@yggdra/shared: types, tarot, diagnosis）
- [x] [id:github] [required] GitHubリポジトリ作成・push `depends-on: setup`

## Phase 1: 実装 `depends-on: setup`

- [x] [id:valhalla] ヴァルハラ デモアプリ（Codex担当）
  - [x] [id:v-diagnosis] 診断フロー（6問、1問ずつ表示、プログレスバー）
  - [x] [id:v-results] 結果画面（TOP3マッチ、相性%、コーチングメッセージ） `depends-on: v-diagnosis`
  - [x] [id:v-profile] ホストプロフィール（タグ、趣味、「仮面と素顔の隙間」） `depends-on: v-results`
  - [x] [id:v-data] ダミーホスト5名のデータ作成
  - [x] [id:v-theme] ダークテーマ（黒/金/紫）適用
- [ ] [id:yggdra] ユグドラ デモアプリ（Gemini担当）
  - [ ] [id:y-diagnosis] 診断フロー（6問、ポップテーマ）
  - [ ] [id:y-select] キャラ選択画面（TOP3 → 推し1人選択） `depends-on: y-diagnosis`
  - [ ] [id:y-tarot] タロット占い（22枚カード、フリップアニメ、1日1回） `depends-on: y-select`
  - [ ] [id:y-oshi] 推しページ（2次元アバター、ステータス） `depends-on: y-select`
  - [ ] [id:y-data] ダミーキャラ5名のデータ作成
  - [ ] [id:y-theme] ポップテーマ（パステルピンク/ラベンダー）適用

## Phase 2: レビュー・統合（Claude担当） `depends-on: valhalla, yggdra`

- [x] [id:review-v] [required] ヴァルハラ コードレビュー
  - [x] 共通パッケージ連携の確認（@yggdra/shared import）
  - [x] UI品質確認（ダークテーマ、モバイルファースト）
  - [x] 診断フロー → 結果 → プロフィールの遷移確認
  - [x] 日本語UI・プライバシー表示の確認
- [ ] [id:review-y] [required] ユグドラ コードレビュー `depends-on: yggdra`
  - [ ] 共通パッケージ連携の確認
  - [ ] タロット占いの動作確認（1日1回制限）
  - [ ] 推し選択フローの確認
- [ ] [id:fix-v] ヴァルハラ指摘事項の修正 `depends-on: review-v`
- [ ] [id:fix-y] ユグドラ指摘事項の修正 `depends-on: review-y`
- [ ] [id:merge] 両ブランチをmainにマージ `depends-on: fix-v, fix-y`
- [ ] [id:build] モノレポ全体のbuild確認 `depends-on: merge`

## Phase 3: ドキュメント同期 `depends-on: merge`

- [ ] [id:docs] [required] ドキュメント更新
  - [ ] CLAUDE.md（プロジェクト用）
  - [ ] README.md

## Phase 4: デプロイ `depends-on: docs`

- [ ] [id:deploy] Vercelにデプロイ（2アプリ）
- [ ] [id:verify] スマホ実機で確認 `depends-on: deploy`

---

## レビュー結果

### ヴァルハラ（Codex成果物）— レビュー完了

**評価: 良好** — MTGデモとして十分な品質

**良い点:**
- `@yggdra/shared` からの型・ロジック連携が正しい
- 診断フロー: スムーズなトランジション（180ms）、プログレスバー、LocalStorage保存
- 結果画面: TOP3表示、相性%、コーチングメッセージ
- プロフィール: 「3秒で刺さる要素」「仮面と素顔の隙間」セクション
- Coming Soon CTA（シャンパンコール、店舗予約）
- 誕生日のプライバシー注記あり
- ダミーデータが多様（5タイプ全て異なる顔/性格/接客スタイル）
- 日本語ラベル変換テーブル完備

**要修正:**
1. フッターに開発用テキスト残存:「375px ベースでそのまま見せられる、MTG 用モバイルデモ。」→ 削除
2. 「仮面と素顔の隙間」テキストが全ホスト共通 → ホストごとに個別化すべき

---

## 完了条件

- [ ] 全タスクが `[x]` に更新されている
- [ ] 両アプリのbuild成功
- [ ] スマホ実機でデモ動作確認
