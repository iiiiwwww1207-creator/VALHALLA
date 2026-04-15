# セキュリティ レビュー

**セキュリティレビュー結果**

**スコア**: B

### 重大な問題 (Critical)
該当なし

### 重要な問題 (High)
該当なし

### 軽微な問題 (Medium)

1. 平文の誕生日が `localStorage` に永続保存される  
ファイル/行: [apps/yggdra/app/diagnosis/page.tsx:25](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:25), [apps/yggdra/app/diagnosis/page.tsx:38](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:38), [apps/yggdra/app/diagnosis/page.tsx:62](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:62), [apps/yggdra/app/diagnosis/page.tsx:73](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:73)  
補足根拠: [apps/yggdra/src/lib/storage.ts:24](/Users/altis/Development/yggdra/apps/yggdra/src/lib/storage.ts:24), [apps/yggdra/app/diagnosis/page.tsx:147](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:147)

問題の説明: `answers` 全体を `saveDiagnosisState()` で保存しており、誕生日回答もそのまま `localStorage` に残ります。`localStorage` は `HttpOnly` にできず、同一オリジン上の JavaScript から読めるため、将来 XSS や第三者スクリプト混入が起きた場合に生年月日が即時に取得可能です。さらに保存期間に制限がなく、共有端末でも残留します。UI 上は「外部には送信されません」とありますが、少なくともローカルには平文で永続化されています。

修正案（誕生日を永続化しない）:
```tsx
const SENSITIVE_QUESTION_IDS = new Set([BIRTHDAY_QUESTION_ID]);

useEffect(() => {
  if (!isReady) return;

  saveDiagnosisState({
    answers: answers.filter((a) => !SENSITIVE_QUESTION_IDS.has(a.questionId)),
  });
}, [answers, isReady]);
```

修正案（保持が必要な場合）:
```ts
// サーバー側で短命セッションに保存し、HttpOnly Cookie で参照
cookies().set('diagnosis_session', encryptedValue, {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  path: '/',
  maxAge: 60 * 30,
});
```

### 推奨事項 (Low)

1. `localStorage` の値をフロー制御に使っているが、認可の代わりにはしないこと  
ファイル/行: [apps/yggdra/app/page.tsx:11](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:11), [apps/yggdra/app/oshi/page.tsx:52](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52)

問題の説明: `loadOshi()` の値で画面遷移や表示分岐をしています。現状は UX 制御なので直ちに脆弱性ではありませんが、`localStorage` はユーザーが任意に改ざん可能です。将来 `/oshi` 配下にユーザー固有データや課金機能を載せる場合、同じ考え方を持ち込むと簡単にバイパスされます。

修正案:
```ts
// 権限や所有者確認はサーバー側で強制する
const session = await getSession();
if (!session?.selectedHostId) {
  redirect('/diagnosis');
}
```

### 補足
この3ファイルでは、`dangerouslySetInnerHTML`、オープンリダイレクト、コマンド/SQL インジェクション、認証情報の直書きは見当たりませんでした。  
ただし、CSP/HSTS/`X-Frame-Options` などのレスポンスヘッダーはページコンポーネントだけでは評価できないため、`middleware.ts`、`next.config.*`、デプロイ設定は別途確認が必要です。
