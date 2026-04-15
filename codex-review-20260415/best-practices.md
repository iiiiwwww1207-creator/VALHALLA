# ベストプラクティス レビュー

**重大な問題 (Critical)**  
該当なし

**重要な問題 (High)**  
1. [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:268) `268-295行目`  
問題: Coming Soon オーバーレイが見た目だけのモーダルです。`role="dialog"`、`aria-modal`、Escape でのクローズ、初期フォーカスがなく、キーボード操作とスクリーンリーダーで使いづらいです。  
修正案:
```tsx
useEffect(() => {
  if (!showComingSoon) return;
  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') setShowComingSoon(false);
  };
  window.addEventListener('keydown', onKeyDown);
  return () => window.removeEventListener('keydown', onKeyDown);
}, [showComingSoon]);

<div role="dialog" aria-modal="true" aria-labelledby="coming-soon-title">
  <h3 id="coming-soon-title">Coming Soon</h3>
```
可能なら Radix UI などのダイアログ実装に寄せるのが安全です。

2. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:109) `109-113, 131-148行目`  
問題: 進捗バーにアクセシビリティ属性がなく、誕生日入力にも明示的なラベルがありません。視覚的には分かっても、支援技術には意図が伝わりません。  
修正案:
```tsx
<div
  role="progressbar"
  aria-valuemin={1}
  aria-valuemax={DIAGNOSIS_QUESTIONS.length}
  aria-valuenow={step + 1}
/>

<label htmlFor="birthday" className="sr-only">{question.text}</label>
<input id="birthday" aria-describedby="birthday-help" type="date" ... />
<p id="birthday-help">誕生日はこの診断だけに使います。</p>
```

**軽微な問題 (Medium)**  
1. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:133) `133行目`  
問題: `new Date().toISOString().split('T')[0]` は UTC 基準です。利用者のローカル日付とずれて、今日を入力できない/未来日を許すケースがあります。  
修正案:
```tsx
const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60_000)
  .toISOString()
  .slice(0, 10);

<input type="date" max={today} ... />
```

2. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:49) `49-55, 117-120行目`  
問題: `setTimeout` のクリーンアップがなく、遷移中も UI がクリック可能です。連打で複数タイマーが積まれ、意図しない遷移や state 更新が起きやすいです。  
修正案:
```tsx
const timeoutRef = useRef<number | null>(null);

useEffect(() => {
  return () => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  };
}, []);

const animateTo = (nextStep: number) => {
  if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  setIsTransitioning(true);
  timeoutRef.current = window.setTimeout(() => {
    setStep(nextStep);
    setIsTransitioning(false);
  }, 180);
};
```
遷移中コンテナに `pointer-events-none` を付けるのも有効です。

3. [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:129) `129-177行目`  
問題: `DiagnosisQuestion['type']` には `'scale'` があるのに、UI は `birthday` とそれ以外しか扱っていません。型の追加に弱く、将来 silent failure になります。  
修正案:
```tsx
switch (question.type) {
  case 'birthday':
    return <BirthdayQuestion ... />;
  case 'select':
    return <SelectQuestion ... />;
  case 'scale':
    return <ScaleQuestion ... />;
  default: {
    const _exhaustive: never = question.type;
    return _exhaustive;
  }
}
```

4. [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:11) `11-22行目`, [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52) `52-65, 102-107行目`  
問題: 主要な表示分岐とリダイレクト判定を `localStorage + useEffect` に寄せているため、初回表示が必ずローディングになり、App Router の RSC/SSR の利点を捨てています。  
修正案:
```tsx
// page.tsx を Server Component に寄せる例
import { cookies } from 'next/headers';

export default async function HomePage() {
  const oshi = (await cookies()).get('oshi')?.value ?? null;
  ...
}
```
ルーティングに効く状態は cookie / server session / URL に持つ方が Next.js の流儀に合います。

**推奨事項 (Low)**  
1. [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:17) `17-43行目`  
問題: ラベル辞書が `Record<string, string>` なので、タグ追加や typo を型で検出できません。  
修正案:
```tsx
import type { FaceType, PersonalityTag, StyleTag } from '@yggdra/shared';

const personalityLabels = { ... } satisfies Record<PersonalityTag, string>;
const styleLabels = { ... } satisfies Record<StyleTag, string>;
const faceLabels = { ... } satisfies Record<FaceType, string>;
```

2. [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:43) `43-74行目`  
問題: CTA の JSX が分岐ごとに重複しています。差分は 1 本目のリンクだけなので、保守時にズレやすいです。  
修正案:
```tsx
const primaryCta = oshi
  ? { href: '/oshi', label: '推しに会いに行く' }
  : { href: '/diagnosis', label: '診断スタート' };
```

総合評価は `B` です。全体として読みやすく実装も素直ですが、アクセシビリティと App Router の使い方に早めに直したい点があります。静的レビューのみで、テストや `lint` は今回は実行していません。
