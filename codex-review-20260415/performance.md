# パフォーマンス レビュー

**パフォーマンスレビュー結果**  
スコア: `B`

**Critical**  
該当なし

**High**  
該当なし

**Medium**
- [apps/yggdra/app/diagnosis/page.tsx:36](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:36)  
  対象行: `36-40`, `61-63`, `72-73`  
  `answers` 更新のたびに `loadDiagnosisState()` と `saveDiagnosisState()` を同期実行しています。`localStorage` はメインスレッドをブロックするので、入力ごとの `read + JSON.parse + write` は体感遅延の原因になります。最終ステップではハンドラ側保存と `useEffect` 側保存が重複しています。  
  修正案:
  ```tsx
  const completedAtRef = useRef<string | undefined>();

  useEffect(() => {
    const stored = loadDiagnosisState();
    completedAtRef.current = stored?.completedAt;
    if (stored?.answers?.length) {
      setAnswers(stored.answers);
      // ...
    }
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady) return;
    const id = window.setTimeout(() => {
      saveDiagnosisState({ answers, completedAt: completedAtRef.current });
    }, 200);
    return () => window.clearTimeout(id);
  }, [answers, isReady]);
  ```
  完了時は `completedAtRef.current` を更新して 1 回だけ保存する形に寄せるのがよいです。

- [apps/yggdra/app/oshi/page.tsx:67](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:67)  
  対象行: `67-100`  
  `/api/nurture` 取得が `cache: 'no-store'` になっており、ページ表示のたびに必ずネットワーク往復が発生します。ステータスが秒単位で変わらないなら、毎回の再訪で不要な待ち時間になります。  
  修正案:
  ```tsx
  const { data } = useSWR(
    character ? `/api/nurture?characterId=${character.id}` : null,
    (url) => fetch(url).then((r) => r.json()),
    { dedupingInterval: 30_000, revalidateOnFocus: false }
  );
  ```
  依存追加を避けるなら、少なくとも `characterId` 単位の簡易メモリキャッシュを置くべきです。

- [apps/yggdra/app/page.tsx:11](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:11)  
  対象行: `11-16`  
  トップページが `localStorage` 読み出し完了まで必ずローディング表示になり、初回描画後に再レンダリングが入ります。ランディングページで毎回 extra paint を発生させる構成です。  
  修正案:
  ```tsx
  // saveOshi 時に cookie にも保存
  document.cookie = `yggdra-oshi-v1=${hostId}; Path=/; Max-Age=31536000`;

  // app/page.tsx を Server Component 化
  import { cookies } from 'next/headers';

  export default async function HomePage() {
    const oshi = (await cookies()).get('yggdra-oshi-v1')?.value ?? null;
    // ...
  }
  ```
  クライアント限定のままなら、全画面ローディングではなく静的シェルを先に描画した方が体感は良くなります。

**Low**
- [apps/yggdra/app/diagnosis/page.tsx:9](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:9)  
  対象行: `9-14`, `28-29`, `43`, `136-137`  
  `upsertAnswer` と `getAnswerValue` が毎回配列走査です。特に復元時の `findIndex` 内から `getAnswerValue` を呼ぶ部分は `O(n²)` です。今は質問数が 6 件なので優先度は低いですが、設問が増えると効いてきます。  
  修正案:
  ```tsx
  type AnswersById = Record<string, string>;

  const [answersById, setAnswersById] = useState<AnswersById>({});
  const selectedValue = answersById[question.id];
  ```
  永続化直前だけ配列に戻せば十分です。

**補足**
- 現状は `DIAGNOSIS_QUESTIONS` も `characters` も小規模なので、最大のボトルネックは配列走査ではなく、同期 `localStorage` I/O と `no-store` による毎回 fetch です。
- 優先順位は `diagnosis` の保存処理整理、次に `home` / `oshi` の初回表示コスト削減です。
