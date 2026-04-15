# UX レビュー

総合スコア: `C`

**重大な問題 (Critical)**
該当なし

**重要な問題 (High)**
1. ファイル: [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:261) (L261-263), [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:24) (L24-31)  
説明: `再診断` の導線なのに既存回答を復元し、全回答済みなら最終設問に戻ります。ユーザーの期待は「最初からやり直す」なので、ラベルと挙動が不一致です。  
修正案: `Link href="/diagnosis?reset=1"` にし、診断側で `if (searchParams.get('reset') === '1') { clearDiagnosisState(); setAnswers([]); setStep(0); }` のように明示的に初期化してください。

2. ファイル: [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:67) (L67-99, L162-208)  
説明: API 失敗時も `OSHI_FALLBACK_STATE` をそのまま表示するため、実データか仮表示かが判別できません。再試行もなく、ユーザーから見ると「それっぽいが信用できない」状態です。  
修正案: `const [statsStatus, setStatsStatus] = useState<'loading'|'ready'|'preview'|'error'>('loading')` を追加し、`preview` なら「プレビュー表示」、`error` なら `再読み込み` ボタンを出してください。

3. ファイル: [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:268) (L268-294)  
説明: 視覚的にはモーダルですが、`role="dialog"`、初期フォーカス、`Esc` で閉じる挙動がありません。キーボード操作時に現在位置や閉じ方が分かりづらく、UX を落とします。  
修正案: `role="dialog" aria-modal="true" aria-labelledby="coming-soon-title"` を付け、`useEffect(() => closeButtonRef.current?.focus(), [showComingSoon])` と `onKeyDown={(e) => e.key === 'Escape' && setShowComingSoon(false)}` を追加してください。

**軽微な問題 (Medium)**
1. ファイル: [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:133) (L131-133)  
説明: `max={new Date().toISOString().split('T')[0]}` は UTC 基準なので、ローカル日付と 1 日ずれる時間帯があります。日付入力の上限が誤り、意図せず選べない日が出ます。  
修正案: `const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().split('T')[0];` として `max={today}` を使ってください。

2. ファイル: [apps/yggdra/app/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:11) (L11-20), [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:24) (L24-34, L80-85), [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52) (L52-65, L102-107)  
説明: 同期的な `localStorage` 読み出しやローカル判定のために毎回フルスクリーンの `読み込み中...` を挟んでおり、初回体験がフラッシュします。処理は軽いのに、体感速度が悪く見えます。  
修正案: 全画面ブロックをやめ、`<main>...{isReady ? content : <Skeleton />}</main>` のように同じレイアウト枠内でスケルトンを出してサイズを固定してください。

3. ファイル: [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:49) (L49-67, L163-171)  
説明: ステップ遷移アニメーション中も選択肢を再タップできるため、「押せたのか分からない」連打を誘発します。短い遷移でも多重操作は UX を不安定にします。  
修正案: `if (isTransitioning) return;` で二重入力を防ぎ、コンテナに `pointer-events-none` を付けて遷移中は操作を止めてください。

**推奨事項 (Low)**
1. ファイル: [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:240) (L240-253, L268-294)  
説明: `もっと見たい！` と `店舗予約` がどちらも同じ `Coming Soon` を返すため、CTA の意味が分かれていません。異なる意図の操作を同じ行き止まりに集約すると、押す価値が下がります。  
修正案: `const [comingSoonType, setComingSoonType] = useState<'details'|'reservation'|null>(null)` のように CTA ごとに文言を出し分け、予約なら `開始時に通知を受け取る` など次の行動を 1 つ置くとよいです。

2. ファイル: [apps/yggdra/app/diagnosis/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:93) (L93-97), [apps/yggdra/app/oshi/page.tsx](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:115) (L115-117, L257-263)  
説明: 戻る系リンクや下部リンクがテキスト密度に対して小さく、モバイルのタップターゲットとしてはやや窮屈です。誤タップや押しづらさが出やすいです。  
修正案: `className="min-h-11 px-3 inline-flex items-center"` のように 44px 前後のヒット領域を確保してください。
