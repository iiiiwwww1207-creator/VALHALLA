# 保守性 レビュー

**重大な問題 (Critical)**
該当なし

**重要な問題 (High)**
- [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:24) `24, 36, 57, 70`
  問題: 診断画面が「状態復元」「永続化」「完了処理」「画面遷移」を同時に持ち、`saveDiagnosisState` が複数経路に分散しています。`completedAt` を effect 内で再読込して維持しているのも暗黙依存です。仕様変更時に修正点が散り、単体テストでも `localStorage` と `router` の両方を毎回モックする必要があります。
  修正案:
  ```tsx
  const {
    step, question, selectedValue, answers,
    selectOption, updateBirthday, submitBirthday, goBack
  } = useDiagnosisFlow({ questions: DIAGNOSIS_QUESTIONS, storage, router });
  ```

- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52) `52-100`
  問題: `loadOshi`、`characters.find`、`router.replace`、`fetch('/api/nurture')` がページ内に直書きされ、UI とデータ取得が密結合です。同系統の処理が `app/nurture/page.tsx` にもあり、レスポンス型も匿名型で重複しています。差分修正やモックが難しく、画面ごとに取得仕様がずれるリスクがあります。
  修正案:
  ```tsx
  const character = useSelectedCharacter(router);
  const nurtureStats = useNurturePreview(character?.id);

  type NurturePreviewResponse =
    Pick<NurtureGetResponse, 'state' | 'databaseAvailable'>;
  ```

**軽微な問題 (Medium)**
- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:17) `17-43`
  問題: `personalityLabels` / `styleLabels` / `faceLabels` がページローカル定義で、同じ辞書が `app/select/page.tsx` にも重複しています。表示名変更のたびに複数画面を同期する必要があり、更新漏れの温床です。
  修正案:
  ```tsx
  export const CHARACTER_LABELS = {
    personality: { tsundere: 'ツンデレ', ... },
    style: { calm: '癒やし', ... },
    face: { korean: '韓国系', ... },
  } as const;
  ```

- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:110) `110-297`
  問題: 1コンポーネントがヘッダ、ヒーロー、ステータス、プロフィール、CTA、モーダルまで持っており責務が広いです。現状でも約300行あり、UI変更時のコンフリクトとセクション単位のテスト難易度が上がります。
  修正案:
  ```tsx
  <OshiHero character={character} />
  <OshiStatusCard stats={nurtureStats} />
  <OshiProfileCard character={character} />
  <ComingSoonModal open={showComingSoon} onClose={closeModal} />
  ```

- [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:49) `49-77, 133`
  問題: `180`、最終設問判定、誕生日の `max` 計算が各所に散在しています。ルール変更時に検索置換ベースになりやすく、変更漏れを起こしやすい構造です。
  修正案:
  ```tsx
  const TRANSITION_MS = 180;
  const isLastStep = step === DIAGNOSIS_QUESTIONS.length - 1;
  const maxBirthday = getTodayDateString();
  ```

**推奨事項 (Low)**
- [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:16) `16-22, 43-74`, [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:80) `80-86`, [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:102) `102-108`
  問題: 全画面ローディングUIとCTAボタンのマークアップが繰り返し書かれています。今は小さいですが、見た目や文言の統一修正がページ単位の手作業になります。
  修正案:
  ```tsx
  <FullscreenLoader message="読み込み中..." />
  <PrimaryAction href={primaryHref}>{primaryLabel}</PrimaryAction>
  ```

**総合評価**
`C`

主因は、ページコンポーネントに副作用とデータ取得が寄りすぎていること、そして画面間で共有すべき辞書・ロードUI・選択キャラクター取得処理が分散していることです。優先度としては `useDiagnosisFlow`、`useSelectedCharacter`、`useNurturePreview` の抽出から始めるのが最も効果的です。
