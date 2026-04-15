# SEO レビュー

**SEO/OGPレビュー結果**  
**スコア**: D

### 重大な問題 (Critical)
該当なし

### 重要な問題 (High)
- [app/page.tsx:8](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:8), [diagnosis/page.tsx:21](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:21), [oshi/page.tsx:49](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:49)  
  `isReady = false` の初期描画中は `読み込み中...` しか返さないため、SSR HTML が薄くなっています。特に `/` は検索流入の主対象なのに、クローラの初回取得で本文が見えない構成です。LCP にも不利です。  
  修正案:
  ```tsx
  // app/page.tsx は Server Component に戻す
  export default function Page() {
    return <HomeClient />;
  }

  // HomeClient 側では本文を最初から描画し、localStorage 依存だけ後から上書きする
  const [oshi, setOshi] = useState<string | null>(null);
  useEffect(() => setOshi(loadOshi()), []);
  ```

- [oshi/page.tsx:52](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:52)  
  `/oshi` は `localStorage` の `oshiId` で内容が変わる 1 URL 多コンテンツです。これではキャラごとの stable URL、canonical、OGP、検索インデックスを作れません。冷スタート時は `/diagnosis` へ飛ぶため、検索向きのページにもなっていません。  
  修正案: SEO 対象にしないなら明示的に `noindex`、SEO 対象にするなら `/oshi/[slug]` へ分割します。
  ```tsx
  // SEO対象にしない場合
  export const metadata = {
    robots: { index: false, follow: false },
  };

  // SEO対象にする場合
  // app/oshi/[slug]/page.tsx + generateMetadata()
  ```

### 重要な問題 (High)
- [layout.tsx:17](/Users/altis/Development/yggdra/apps/yggdra/app/layout.tsx:17), [page.tsx:1](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:1), [diagnosis/page.tsx:1](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:1), [oshi/page.tsx:1](/Users/altis/Development/yggdra/apps/yggdra/app/oshi/page.tsx:1)  
  3ページとも `use client` のためページ単位の `metadata` を持てず、全ページが共通 title/description を継承しています。検索結果でタイトル重複が起き、意図の異なる `/`・`/diagnosis`・`/oshi` を区別できません。  
  修正案:
  ```tsx
  // app/diagnosis/page.tsx を Server Component にして metadata を定義
  export const metadata = {
    title: '推し診断 | ユグドラ',
    description: '質問に答えて、あなたに合う推しアイドルを見つける診断ページ。',
  };

  export default function Page() {
    return <DiagnosisClient />;
  }
  ```

- [layout.tsx:17](/Users/altis/Development/yggdra/apps/yggdra/app/layout.tsx:17)  
  `canonical`、`metadataBase`、`openGraph`、`twitter` が未設定です。SNS シェア品質が低く、URL 正規化もできていません。  
  修正案:
  ```tsx
  export const metadata = {
    metadataBase: new URL('https://example.com'),
    title: { default: 'ユグドラ', template: '%s | ユグドラ' },
    alternates: { canonical: '/' },
    openGraph: {
      siteName: 'ユグドラ',
      locale: 'ja_JP',
      type: 'website',
      images: [{ url: '/og/default.png', width: 1200, height: 630 }],
    },
    twitter: { card: 'summary_large_image' },
  };
  ```

- `apps/yggdra/app/robots.ts` 未作成  
  `robots.txt` 相当が見当たりません。開発中のままでもクロール制御が曖昧です。  
  修正案:
  ```ts
  export default function robots() {
    return {
      rules: { userAgent: '*', allow: '/' },
      sitemap: 'https://example.com/sitemap.xml',
    };
  }
  ```

### 軽微な問題 (Medium)
- [diagnosis/page.tsx:122](/Users/altis/Development/yggdra/apps/yggdra/app/diagnosis/page.tsx:122)  
  ページ内の最上位見出しが `h2` で、`h1` がありません。診断ページの主題をクローラに渡しにくいです。  
  修正案:
  ```tsx
  <h1 className="sr-only">推し診断</h1>
  <h2>{question.text}</h2>
  ```

- `apps/yggdra/app/sitemap.ts` 未作成  
  `sitemap.xml` 相当が見当たりません。小規模サイトでも検索エンジンへの URL 発見性は落ちます。  
  修正案:
  ```ts
  export default function sitemap() {
    return [
      { url: 'https://example.com/' },
      { url: 'https://example.com/diagnosis' },
    ];
  }
  ```

### 推奨事項 (Low)
- [app/page.tsx:24](/Users/altis/Development/yggdra/apps/yggdra/app/page.tsx:24)  
  ホームが集客ランディングページなら、`WebSite` の JSON-LD を追加すると検索理解が安定します。  
  修正案:
  ```tsx
  <script
    type="application/ld+json"
    dangerouslySetInnerHTML={{ __html: JSON.stringify({ '@context': 'https://schema.org', '@type': 'WebSite', name: 'ユグドラ', url: 'https://example.com' }) }}
  />
  ```

- [layout.tsx:19](/Users/altis/Development/yggdra/apps/yggdra/app/layout.tsx:19)  
  description が「デモアプリ」で終わっており、検索意図に対して弱いです。指名外流入を狙うなら「推し診断」「アイドル診断」「相性診断」などの主要語を自然に含めた説明にした方がよいです。  
  修正案: `あなたに合う推しアイドルを診断し、育成や占いも楽しめるアプリ。`

補足: 確認できた `metadata` 定義は [layout.tsx:17](/Users/altis/Development/yggdra/apps/yggdra/app/layout.tsx:17) のみで、`robots.ts`、`sitemap.ts`、`opengraph-image`、`twitter-image` は見当たりませんでした。検索流入を本気で取りに行くなら、最優先は「SSR で本文を出すこと」と「`/oshi` を stable URL 化すること」です。
