# エラーハンドリング レビュー

総合評価: `D`

ローカルストレージ例外と未設定のエラー境界が重なっており、環境依存の失敗がそのまま画面クラッシュに繋がります。

**重大な問題 (Critical)**
該当なし

**重要な問題 (High)**
1. ファイル: [apps/yggdra/app/diagnosis/page.tsx:24](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:24)  
問題: `loadDiagnosisState()` / `saveDiagnosisState()` の失敗をこのページ側で処理していません。保存処理は 38, 62, 73 行目でも同様です。実装元の [apps/yggdra/src/lib/storage.ts:15](/Users/altis/Development/yggdra/apps/yggdra/src/lib/storage.ts:15), [apps/yggdra/src/lib/storage.ts:26](/Users/altis/Development/yggdra/apps/yggdra/src/lib/storage.ts:26) では `localStorage.getItem/setItem` 自体は保護されていないため、`SecurityError` / `QuotaExceededError` で診断画面がクラッシュし得ます。  
修正案:
```tsx
useEffect(() => {
  try {
    const stored = loadDiagnosisState();
    if (Array.isArray(stored?.answers)) {
      setAnswers(stored.answers);
    }
  } catch (error) {
    console.error('Failed to restore diagnosis state', error);
    setError('保存データを読み込めませんでした。');
    setAnswers([]);
    setStep(0);
  } finally {
    setIsReady(true);
  }
}, []);

const persistAndGoNext = (nextAnswers: DiagnosisAnswer[]) => {
  try {
    saveDiagnosisState({ answers: nextAnswers, completedAt: new Date().toISOString() });
    router.push('/select');
  } catch (error) {
    console.error('Failed to save diagnosis state', error);
    setError('回答を保存できませんでした。もう一度お試しください。');
  }
};
```

2. ファイル: [apps/yggdra/app/page.tsx:11](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:11), [apps/yggdra/app/oshi/page.tsx:52](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52)  
問題: `loadOshi()` の例外を考慮していません。`localStorage` が使えない環境ではトップ画面と推し画面の初期化がそのまま失敗します。特に `oshi/page.tsx` は復旧導線が `router.replace()` しかなく、例外時の代替 UI もありません。  
修正案:
```tsx
useEffect(() => {
  try {
    const oshiId = loadOshi();
    setOshi(oshiId);
  } catch (error) {
    console.error('Failed to load oshi', error);
    setOshi(null);
    setStorageError('保存データを読み込めませんでした。');
  } finally {
    setIsReady(true);
  }
}, []);
```

3. ファイル: [apps/yggdra/app/page.tsx:7](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:7), [apps/yggdra/app/diagnosis/page.tsx:17](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:17), [apps/yggdra/app/oshi/page.tsx:45](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:45)  
問題: これらはすべてクライアントページですが、`apps/yggdra/app` 配下に `error.tsx` / `global-error.tsx` がありません。上記の storage/fetch 例外が未処理のまま上がると、ユーザーフレンドリーな復旧 UI なしでルート単位に落ちます。  
修正案:
```tsx
// apps/yggdra/app/error.tsx
'use client';
import { useEffect } from 'react';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    console.error(error);
    // Sentry.captureException(error);
  }, [error]);

  return <button onClick={reset}>再試行</button>;
}
```

**軽微な問題 (Medium)**
1. ファイル: [apps/yggdra/app/oshi/page.tsx:73](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:73)  
問題: `fetch` 失敗時と `response.ok === false` の両方を実質握り潰しています。`catch {}` は空で、HTTP エラー時も `return` するだけなので、ユーザーは「取得失敗」なのか「静的プレビュー表示」なのか区別できません。  
修正案:
```tsx
try {
  const response = await fetch(...);
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    setStatsError(data?.error ?? '育成データを取得できませんでした。');
    return;
  }
} catch (error) {
  if (error instanceof DOMException && error.name === 'AbortError') return;
  console.error('Failed to load nurture stats', error);
  setStatsError('育成データを取得できませんでした。');
}
```

2. ファイル: [apps/yggdra/app/diagnosis/page.tsx:25](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:25)  
問題: `loadDiagnosisState()` の戻り値を構造検証せずに使っています。`stored?.answers?.length` だけでは不十分で、壊れた JSON や旧バージョン形式が入ると `getAnswerValue(stored.answers, ...)` で実行時例外になります。  
修正案:
```tsx
const stored = loadDiagnosisState();
if (!stored || !Array.isArray(stored.answers)) {
  setAnswers([]);
  setStep(0);
  return;
}
```
```tsx
// 可能なら Zod
const StoredDiagnosisStateSchema = z.object({
  answers: z.array(z.object({ questionId: z.string(), value: z.string() })),
  completedAt: z.string().optional(),
});
```

**推奨事項 (Low)**
1. ファイル: [apps/yggdra/app/oshi/page.tsx:75](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:75)  
問題: `AbortController` は unmount 時しか使っておらず、通信ハング時のタイムアウトがありません。失敗時も静的プレビューのままなので、遅延と障害の区別がつきません。  
修正案:
```tsx
const controller = new AbortController();
const timeoutId = window.setTimeout(() => controller.abort(), 5000);
try {
  const response = await fetch(url, { signal: controller.signal, cache: 'no-store' });
} finally {
  window.clearTimeout(timeoutId);
}
```

2. ファイル: [apps/yggdra/app/oshi/page.tsx:84](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:84)  
問題: `response.json()` を型アサーションだけで信頼しています。API 形状が崩れても `state` の中身は未検証で、UI に不正値が入る可能性があります。  
修正案:
```tsx
const NurtureResponseSchema = z.object({
  databaseAvailable: z.boolean().optional(),
  state: z.object({
    level: z.number(),
    intimacy: z.number(),
    mood: z.number(),
  }).optional(),
});

const parsed = NurtureResponseSchema.safeParse(await response.json());
if (!parsed.success) {
  setStatsError('育成データの形式が不正です。');
  return;
}
```

最優先は `diagnosis/page.tsx` と `page.tsx` / `oshi/page.tsx` の `localStorage` 例外対策、その次が `app/error.tsx` の追加です。ここを直すだけで「白画面になる失敗」はかなり減ります。
