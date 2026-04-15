# コード品質 レビュー

**コード品質レビュー**

**スコア**: B  
全体として UI 実装は素直ですが、状態遷移の重複、例外処理の弱さ、型の境界が曖昧な点が保守性を下げています。

### 重大な問題 (Critical)
該当なし

### 重要な問題 (High)
- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:267) `267-295行目`  
  問題: `Coming Soon` のオーバーレイが `div` ベースの独自実装で、`role="dialog"`、`aria-modal`、Escape 閉じ、フォーカス管理がありません。見た目は動きますが、アクセシビリティと再利用性の両面で負債になりやすいです。  
  修正案:
  ```tsx
  <Dialog open={showComingSoon} onOpenChange={setShowComingSoon}>
    <DialogContent aria-describedby="coming-soon-description">
      <DialogTitle>Coming Soon</DialogTitle>
      <DialogDescription id="coming-soon-description">
        この機能は現在準備中です。お楽しみに！
      </DialogDescription>
    </DialogContent>
  </Dialog>
  ```

### 軽微な問題 (Medium)
- [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:57) `57-78行目`  
  問題: 完了処理と次ステップ遷移が `handleSelectOption` と `handleBirthdaySubmit` に重複しています。仕様変更時に分岐の片方だけ直すリスクがあります。  
  修正案:
  ```tsx
  const LAST_STEP = DIAGNOSIS_QUESTIONS.length - 1;

  const completeDiagnosis = (nextAnswers: DiagnosisAnswer[]) => {
    saveDiagnosisState({ answers: nextAnswers, completedAt: new Date().toISOString() });
    router.push('/select');
  };
  ```

- [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:49) `49-54行目`  
  問題: `180` がマジックナンバーで、`setTimeout` もクリーンアップされていません。遷移ロジックの意図が読み取りにくく、将来の変更やアンマウント時の挙動を追いづらいです。  
  修正案:
  ```tsx
  const TRANSITION_MS = 180;
  const transitionTimerRef = useRef<number | null>(null);

  useEffect(() => () => transitionTimerRef.current && clearTimeout(transitionTimerRef.current), []);
  ```

- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:73) `73-94行目`  
  問題: `catch {}` が実質的に空で、Abort 以外の失敗も握りつぶしています。デバッグ性が低く、障害時に原因を追いづらいです。  
  修正案:
  ```tsx
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') return;
    console.error('Failed to load nurture stats', error);
  }
  ```

- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:84) `84-87行目`  
  問題: `response.json()` の戻り値をその場の `as` で型断言しており、API 側との契約ズレを静かに見逃します。クライアントと API の型契約は共有した方が保守しやすいです。  
  修正案:
  ```tsx
  import type { NurtureApiResponse } from '@yggdra/shared';

  const data: NurtureApiResponse = await response.json();
  ```

### 推奨事項 (Low)
- [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:17) `17-43行目`  
  問題: `Record<string, string>` だとラベル辞書のキー typo や不足を型で拾えません。  
  修正案: `const personalityLabels = {...} as const satisfies Record<PersonalityTag, string>;`

- [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:43) `43-74行目`  
  問題: CTA の分岐で `tarot` リンクと大半のマークアップが重複しています。  
  修正案: `const primaryCta = oshi ? { href: '/oshi', label: '推しに会いに行く' } : { href: '/diagnosis', label: '診断スタート' };`

- [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:44) `44-47行目`  
  問題: 単純な算術に `useMemo` を使っており、可読性の割に効果が薄いです。  
  修正案: `const progressPercent = ((step + 1) / DIAGNOSIS_QUESTIONS.length) * 100;`

**前提 / 補足**
- `loadOshi` / `loadDiagnosisState` は `localStorage` ラッパー想定でレビューしています。
- `@yggdra/shared` 側にタグや API レスポンスの共有型を置ける前提で型改善案を書いています。
