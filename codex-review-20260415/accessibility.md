# アクセシビリティ レビュー

**アクセシビリティレビュー結果**

**スコア**: D  
行番号は提示されたコードを基準にしています。主な懸念は、診断フローのフォーム意味付け不足と、モーダルのキーボード/スクリーンリーダー対応不足です。

### 重大な問題 (Critical)
該当なし

### 重要な問題 (High)
1. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:131) 131-147  
`type="date"` の入力にプログラム上のラベルがありません。見出しテキストと補足文も `input` に関連付いていないため、スクリーンリーダーでは「何を入力する欄か」「補足説明があるか」が伝わりません。`WCAG 1.3.1 / 3.3.2`

```tsx
const titleId = `question-${question.id}`;
const helpId = `help-${question.id}`;
const inputId = `input-${question.id}`;

<h1 id={titleId} className="font-display text-2xl font-bold">
  {question.text}
</h1>
<input
  id={inputId}
  type="date"
  aria-labelledby={titleId}
  aria-describedby={helpId}
  ...
/>
<p id={helpId}>誕生日はこの診断だけに使います。外部には送信されません。</p>
```

2. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:159) 159-174  
選択肢が見た目上は単一選択ですが、実装はただの `button` 群です。スクリーンリーダーには「何個の選択肢があるか」「今どれが選択済みか」が伝わりません。`WCAG 1.3.1 / 4.1.2`

```tsx
<fieldset>
  <legend className="sr-only">{question.text}</legend>
  {question.options?.map((option) => (
    <label key={option.value} className="...">
      <input
        type="radio"
        name={question.id}
        value={option.value}
        checked={selectedValue === option.value}
        onChange={() => handleSelectOption(option.value)}
      />
      <span>{option.label}</span>
    </label>
  ))}
</fieldset>
```

3. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:49) 49-55, 103-123  
質問遷移時にフォーカス移動もライブ通知もありません。ボタン押下後に内容だけが差し替わるため、キーボード/スクリーンリーダー利用者は「次の質問へ進んだ」ことを把握しづらいです。`WCAG 2.4.3 / 4.1.3`

```tsx
const headingRef = useRef<HTMLHeadingElement>(null);

useEffect(() => {
  if (isReady) headingRef.current?.focus();
}, [step, isReady]);

<h1 ref={headingRef} tabIndex={-1}>{question.text}</h1>
<p className="sr-only" aria-live="polite">
  質問 {step + 1} / {DIAGNOSIS_QUESTIONS.length}
</p>
<progress value={step + 1} max={DIAGNOSIS_QUESTIONS.length} />
```

4. [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:268) 268-295  
`Coming Soon` オーバーレイがアクセシブルなダイアログになっていません。`role="dialog"`、`aria-modal`、ラベル付け、初期フォーカス、`Escape` 閉じる、フォーカス戻しがないため、支援技術利用者には扱いにくい実装です。`WCAG 2.1.1 / 2.4.3 / 4.1.2`

```tsx
<div className="fixed inset-0 ..." role="presentation">
  <div
    role="dialog"
    aria-modal="true"
    aria-labelledby="coming-soon-title"
    aria-describedby="coming-soon-desc"
    onKeyDown={(e) => e.key === 'Escape' && setShowComingSoon(false)}
  >
    <h2 id="coming-soon-title">Coming Soon</h2>
    <p id="coming-soon-desc">この機能は現在準備中です。お楽しみに！</p>
    <button autoFocus onClick={() => setShowComingSoon(false)}>閉じる</button>
  </div>
</div>
```

### 軽微な問題 (Medium)
1. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:122) 122  
診断ページの最初の見出しが `h2` から始まっています。ページの主見出しがないため、見出しナビゲーションの整合性が落ちます。`WCAG 1.3.1 / 2.4.6`

```tsx
<h1 className="font-display text-2xl font-bold text-foreground">
  {question.text}
</h1>
```

2. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:83), [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:105), [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:19)  
`読み込み中...` が単なるテキストで、状態変化として通知されません。非同期ロード中は `role="status"` と `aria-live` を付けたほうが安定します。`WCAG 4.1.3`

```tsx
<main aria-busy="true" ...>
  <div role="status" aria-live="polite">読み込み中...</div>
</main>
```

### 推奨事項 (Low)
1. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:98), [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:119), [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:30)  
装飾目的の `svg` に `aria-hidden` がありません。音声読み上げで不要なノイズになることがあります。`WCAG 1.1.1`

```tsx
<svg aria-hidden="true" focusable="false" ...>
```

2. [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:145) 145-159, [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:216) 216-228  
タグ群とプロフィール詳細が `div`/`span` ベースで、構造情報が弱いです。タグは `ul/li`、プロフィールは `dl/dt/dd` にすると支援技術で意味が伝わりやすくなります。`WCAG 1.3.1`

```tsx
<ul>{character.personalityTags.map((tag) => <li key={tag}>{tag}</li>)}</ul>

<dl>
  <dt>趣味</dt>
  <dd>{character.hobbies.join('、')}</dd>
</dl>
```

未確認事項として、`bg-primary` や `text-muted-foreground` の実際のコントラスト比はトークン値が見えていないため判定していません。また、`AvatarPlaceholder` の内部実装は未提示なので、代替テキストや画像ロールの妥当性は別途確認が必要です。
