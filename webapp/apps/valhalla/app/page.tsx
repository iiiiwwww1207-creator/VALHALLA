'use client';

import Link from 'next/link';

const features = [
  {
    id: 'glossary',
    num: '01',
    en: 'Glossary',
    title: 'ホスト用語説明集',
    catch: 'まずはホストクラブの\n基本を知っておこう',
    bridge: '用語がわかったら、次は自分に合うキャストを探してみよう',
    href: '/glossary',
  },
  {
    id: 'matching',
    num: '02',
    en: 'Matching',
    title: '相性診断',
    catch: '生年月日から\n運命のキャストを探す',
    bridge: '気になるキャストが見つかったら、料金の目安を確認してみよう',
    href: '/matching',
  },
  {
    id: 'simulator',
    num: '03',
    en: 'Price Simulator',
    title: '料金シミュレーター',
    catch: '来店前に\n料金の目安を確認',
    bridge: '予算のイメージができたら、占いで背中を押してもらおう',
    href: '/simulator',
  },
  {
    id: 'tarot',
    num: '04',
    en: 'Tarot',
    title: 'タロット占い',
    catch: '人気キャストに\n今日の運勢を占ってもらう',
    bridge: 'いい運勢が出たら、シャンパンコールの世界を覗いてみよう',
    href: '/tarot',
  },
  {
    id: 'champagne',
    num: '05',
    en: 'Champagne Call',
    title: 'シャンパンコール動画',
    catch: '実際の盛り上がりを\n体感してから行こう',
    bridge: null,
    href: '/champagne',
  },
];

export default function HomePage() {
  return (
    <main className="min-h-dvh bg-[#07050A] text-[#F5EFE0] overflow-x-hidden" style={{ fontFamily: 'var(--font-body)' }}>

      {/* ===== HERO ===== */}
      <section className="relative h-dvh min-h-[680px] flex flex-col overflow-hidden">
        <div className="absolute inset-0 z-0 flex">
          <div className="flex-1 relative overflow-hidden">
            <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" style={{ filter: 'saturate(1.05) brightness(1.0)' }}>
              <source src="https://github.com/iiiiwwww1207-creator/VALHALLA/releases/download/teaser-v1/valhalla_morning.mp4" type="video/mp4" />
            </video>
          </div>
          <div className="flex-1 relative overflow-hidden">
            <video autoPlay muted loop playsInline className="absolute inset-0 w-full h-full object-cover" style={{ filter: 'saturate(0.9) brightness(0.85)' }}>
              <source src="https://github.com/iiiiwwww1207-creator/VALHALLA/releases/download/teaser-v1/valhalla_night.mp4" type="video/mp4" />
            </video>
          </div>
        </div>
        <div className="absolute inset-0 z-10" style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.5) 100%), linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.05) 30%, rgba(0,0,0,0.85) 100%)' }} />
        <div className="absolute top-0 bottom-0 left-1/2 w-px z-20" style={{ background: 'linear-gradient(180deg, transparent 0%, rgba(201,169,97,0.25) 15%, rgba(201,169,97,0.7) 50%, rgba(201,169,97,0.25) 85%, transparent 100%)', transform: 'translateX(-50%)' }} />
        <div className="relative z-30 flex-1 flex flex-col items-center justify-between px-6 pt-14 pb-10 max-w-[480px] mx-auto w-full">
          <div className="border border-[rgba(201,169,97,0.6)] px-5 py-1.5" style={{ background: 'rgba(7,5,10,0.6)', backdropFilter: 'blur(8px)' }}>
            <span className="text-[9px] tracking-[0.6em] text-[#C9A961] uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>Group Yggdrasill</span>
          </div>
          <div className="text-center">
            <p className="text-[9px] tracking-[0.6em] text-[rgba(201,169,97,0.7)] mb-3 uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>Group Yggdrasill</p>
            <h1 className="leading-none font-medium text-[#E8CB85]" style={{ fontFamily: 'var(--font-display)', fontSize: '80px', textShadow: '0 0 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,169,97,0.4)', letterSpacing: '0.06em' }}>YGD</h1>
            <div className="mt-4 flex items-center gap-3">
              <div className="h-px flex-1 bg-[rgba(201,169,97,0.3)]" />
              <span className="text-xs tracking-[0.2em] text-[rgba(245,239,224,0.7)]">ヴァルハラ公式アプリ</span>
              <div className="h-px flex-1 bg-[rgba(201,169,97,0.3)]" />
            </div>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-[8px] tracking-[0.5em] text-[rgba(201,169,97,0.5)] uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>scroll</span>
            <div className="w-px h-8 bg-gradient-to-b from-[rgba(201,169,97,0.5)] to-transparent" />
          </div>
        </div>
      </section>

      {/* ===== メニューセクション ===== */}
      <section className="max-w-[480px] mx-auto bg-[#07050A]">
        <div className="h-px bg-gradient-to-r from-transparent via-[rgba(201,169,97,0.4)] to-transparent" />

        <div className="px-6 pt-8 pb-2">
          <p className="text-[9px] tracking-[0.6em] text-[rgba(201,169,97,0.5)] uppercase mb-1" style={{ fontFamily: 'var(--font-cinzel)' }}>Select</p>
          <h2 className="text-2xl font-bold tracking-[0.3em] text-[#E8CB85]" style={{ fontFamily: 'var(--font-cinzel)' }}>MENU</h2>
        </div>

        {/* ジャーニーレイアウト */}
        <div className="pb-10">
          {features.map((f, i) => {
            const isRight = i % 2 === 1;
            return (
              <div key={f.id}>
                {/* メニューアイテム */}
                <Link href={f.href}>
                  <div className={`group relative overflow-hidden border-t border-[rgba(201,169,97,0.2)] transition-all duration-300 hover:bg-[rgba(201,169,97,0.06)] ${i === features.length - 1 && !f.bridge ? 'border-b border-[rgba(201,169,97,0.2)]' : ''}`}>

                    {/* 背景番号 */}
                    <div className={`absolute top-1/2 -translate-y-1/2 text-[90px] font-bold text-[rgba(201,169,97,0.04)] leading-none select-none pointer-events-none ${isRight ? 'right-3' : 'left-3'}`}
                      style={{ fontFamily: 'var(--font-cinzel)' }}>
                      {f.num}
                    </div>

                    <div className={`relative px-6 py-7 flex flex-col ${isRight ? 'items-end text-right' : 'items-start text-left'}`}>

                      {/* 英語ラベル＋番号 */}
                      <div className={`flex items-center gap-3 mb-2 ${isRight ? 'flex-row-reverse' : ''}`}>
                        <span className="text-[9px] tracking-[0.5em] text-[rgba(201,169,97,0.5)] uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>
                          {f.en}
                        </span>
                        <div className="w-4 h-px bg-[rgba(201,169,97,0.3)]" />
                        <span className="text-[9px] text-[rgba(201,169,97,0.35)]" style={{ fontFamily: 'var(--font-cinzel)' }}>
                          {f.num}
                        </span>
                      </div>

                      {/* 日本語タイトル */}
                      <h3 className="inline-block text-[20px] font-bold text-[#E8CB85] leading-tight mb-2 tracking-wide border border-[rgba(201,169,97,0.5)] px-3 py-1" style={{ background: 'rgba(201,169,97,0.05)' }}>
                        {f.title}
                      </h3>

                      {/* キャッチコピー */}
                      <p className="text-[11px] text-[rgba(245,239,224,0.4)] leading-6 whitespace-pre-line tracking-wider">
                        {f.catch}
                      </p>

                      {/* 矢印 */}
                      <div className={`mt-4 flex items-center gap-2 ${isRight ? 'flex-row-reverse' : ''}`}>
                        <div className="w-6 h-px bg-[rgba(201,169,97,0.4)] group-hover:w-10 transition-all duration-300" />
                        <span className="text-[10px] text-[rgba(201,169,97,0.5)] group-hover:text-[#C9A961] transition-colors" style={{ fontFamily: 'var(--font-cinzel)' }}>
                          {isRight ? '←' : '→'}
                        </span>
                      </div>
                    </div>

                    {/* アクセントライン */}
                    <div className={`absolute top-0 bottom-0 w-0.5 bg-gradient-to-b from-transparent via-[rgba(201,169,97,0.4)] to-transparent group-hover:via-[rgba(201,169,97,0.9)] transition-all duration-300 origin-center ${isRight ? 'right-0' : 'left-0'}`} />
                  </div>
                </Link>

                {/* ブリッジテキスト（次のステップへの誘導） */}
                {f.bridge && (
                  <div className="relative flex flex-col items-center py-4 px-8">
                    {/* 上の縦線 */}
                    <div className="w-px h-4 bg-gradient-to-b from-[rgba(201,169,97,0.3)] to-[rgba(201,169,97,0.15)]" />
                    {/* テキスト */}
                    <p className="text-center text-[10px] text-[rgba(245,239,224,0.35)] tracking-widest leading-5 py-2 px-4 border-l border-r border-[rgba(201,169,97,0.1)]">
                      {f.bridge}
                    </p>
                    {/* 下の縦線＋矢印 */}
                    <div className="w-px h-4 bg-gradient-to-b from-[rgba(201,169,97,0.15)] to-[rgba(201,169,97,0.3)]" />
                    <div className="text-[rgba(201,169,97,0.4)] text-[8px]">▼</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="text-center pb-10">
          <div className="h-px bg-gradient-to-r from-transparent via-[rgba(201,169,97,0.15)] to-transparent mb-6" />
          <p className="text-[9px] tracking-[0.4em] text-[rgba(245,239,224,0.2)] uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>© 2026 Group Yggdrasill</p>
        </div>
      </section>
    </main>
  );
}
