'use client';

import Link from 'next/link';
import { CAST_PUBLIC } from '../src/data/cast-public';

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

const GOLD = '#C9A961';
const GOLD_DIM = 'rgba(201,169,97,0.5)';
const GOLD_FAINT = 'rgba(201,169,97,0.1)';
const CREAM = '#F5EFE0';
const CREAM_DIM = 'rgba(245,239,224,0.4)';
const CREAM_FAINT = 'rgba(245,239,224,0.35)';
const DARK = '#07050A';
const GOLD_BRIGHT = '#E8CB85';

// GitHub Pages では /VALHALLA/ プレフィックスが必要
const BASE = process.env.NODE_ENV === 'production' ? '/VALHALLA' : '';

// キャスト写真（画像あるものだけ）をシャッフルして使う
const CAST_IMAGES = CAST_PUBLIC.filter(c => c.image).map(c => `${BASE}${c.image}`);

// マーキー用に十分な枚数に複製
function buildRow(offset: number, count: number) {
  const all = [...CAST_IMAGES].sort(() => (offset * 17 + 7) % 3 - 1);
  const repeated: string[] = [];
  while (repeated.length < count) repeated.push(...all);
  return repeated.slice(0, count);
}

export default function HomePage() {
  const row1 = buildRow(0, 30);
  const row2 = buildRow(1, 30);
  const row3 = buildRow(2, 30);
  return (
    <main style={{ minHeight: '100dvh', backgroundColor: DARK, color: CREAM, overflowX: 'hidden', fontFamily: 'var(--font-body)' }}>

      {/* ===== HERO ===== */}
      <section style={{ position: 'relative', height: '100dvh', minHeight: '680px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, zIndex: 0, display: 'flex' }}>
          <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
            <video autoPlay muted loop playsInline style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(1.05) brightness(1.0)' }}>
              <source src="https://github.com/iiiiwwww1207-creator/VALHALLA/releases/download/teaser-v1/valhalla_morning.mp4" type="video/mp4" />
            </video>
          </div>
          <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
            <video autoPlay muted loop playsInline style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', filter: 'saturate(0.9) brightness(0.85)' }}>
              <source src="https://github.com/iiiiwwww1207-creator/VALHALLA/releases/download/teaser-v1/valhalla_night.mp4" type="video/mp4" />
            </video>
          </div>
        </div>
        <div style={{ position: 'absolute', inset: 0, zIndex: 10, background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.5) 100%), linear-gradient(180deg, rgba(0,0,0,0.25) 0%, rgba(0,0,0,0.05) 30%, rgba(0,0,0,0.85) 100%)' }} />
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '50%', width: '1px', zIndex: 20, background: 'linear-gradient(180deg, transparent 0%, rgba(201,169,97,0.25) 15%, rgba(201,169,97,0.7) 50%, rgba(201,169,97,0.25) 85%, transparent 100%)', transform: 'translateX(-50%)' }} />
        <div style={{ position: 'relative', zIndex: 30, flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between', padding: '56px 24px 40px', maxWidth: '480px', margin: '0 auto', width: '100%' }}>
          <div style={{ border: `1px solid rgba(201,169,97,0.6)`, padding: '6px 20px', background: 'rgba(7,5,10,0.6)', backdropFilter: 'blur(8px)' }}>
            <span style={{ fontSize: '9px', letterSpacing: '0.6em', color: GOLD, textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>Group Yggdrasill</span>
          </div>
          <div style={{ textAlign: 'center' }}>
            <p style={{ fontSize: '9px', letterSpacing: '0.6em', color: 'rgba(201,169,97,0.7)', marginBottom: '12px', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>Group Yggdrasill</p>
            <h1 style={{ lineHeight: 1, fontWeight: 500, color: GOLD_BRIGHT, fontFamily: 'var(--font-display)', fontSize: '80px', textShadow: '0 0 40px rgba(0,0,0,0.8), 0 0 20px rgba(201,169,97,0.4)', letterSpacing: '0.06em' }}>YGD</h1>
            <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ height: '1px', flex: 1, backgroundColor: 'rgba(201,169,97,0.3)' }} />
              <span style={{ fontSize: '12px', letterSpacing: '0.2em', color: 'rgba(245,239,224,0.7)' }}>ヴァルハラ公式アプリ</span>
              <div style={{ height: '1px', flex: 1, backgroundColor: 'rgba(201,169,97,0.3)' }} />
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
            <span style={{ fontSize: '8px', letterSpacing: '0.5em', color: 'rgba(201,169,97,0.5)', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>scroll</span>
            <div style={{ width: '1px', height: '32px', background: 'linear-gradient(to bottom, rgba(201,169,97,0.5), transparent)' }} />
          </div>
        </div>
      </section>

      <style>{`
        @keyframes mqLeft  { 0% { transform: translateX(0); }    100% { transform: translateX(-50%); } }
        @keyframes mqRight { 0% { transform: translateX(-50%); } 100% { transform: translateX(0); } }
        .mq-left   { animation: mqLeft  45s linear infinite; display: flex; gap: 4px; width: max-content; }
        .mq-left2  { animation: mqLeft  60s linear infinite; display: flex; gap: 4px; width: max-content; }
        .mq-right  { animation: mqRight 52s linear infinite; display: flex; gap: 4px; width: max-content; }
      `}</style>

      {/* ===== MENU ===== */}
      <section style={{ maxWidth: '480px', margin: '0 auto', backgroundColor: DARK }}>
        <div style={{ height: '1px', background: 'linear-gradient(to right, transparent, rgba(201,169,97,0.4), transparent)' }} />

        <div style={{ padding: '32px 24px 8px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.6em', color: GOLD_DIM, textTransform: 'uppercase', marginBottom: '4px', fontFamily: 'var(--font-cinzel)' }}>Select</p>
          <h2 style={{ fontSize: '24px', fontWeight: 700, letterSpacing: '0.3em', color: GOLD_BRIGHT, fontFamily: 'var(--font-cinzel)' }}>MENU</h2>
        </div>

        <div style={{ paddingBottom: '40px' }}>
          {features.map((f, i) => {
            const isRight = i % 2 === 1;
            return (
              <div key={f.id}>
                <Link href={f.href} style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}>
                  <div style={{ position: 'relative', overflow: 'hidden', borderTop: `1px solid rgba(201,169,97,0.2)`, ...(i === features.length - 1 && !f.bridge ? { borderBottom: `1px solid rgba(201,169,97,0.2)` } : {}) }}>

                    {/* 相性診断のみ：カード全体に薄い写真マーキー背景 */}
                    {f.id === 'matching' && (
                      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
                        {[
                          { row: row1, cls: 'mq-left',  top: '0%' },
                          { row: row2, cls: 'mq-right', top: '33.33%' },
                          { row: row3, cls: 'mq-left2', top: '66.66%' },
                        ].map(({ row, cls, top }) => (
                          <div key={top} style={{ position: 'absolute', left: 0, top, width: '100%', height: '33.34%', overflow: 'hidden' }}>
                            <div className={cls}>
                              {[...row, ...row].map((img, idx) => (
                                <img key={idx} src={img} alt="" style={{ flexShrink: 0, width: '56px', height: '100%', objectFit: 'cover', objectPosition: 'center 15%', display: 'block' }} />
                              ))}
                            </div>
                          </div>
                        ))}
                        {/* 暗めオーバーレイ（薄め） */}
                        <div style={{ position: 'absolute', inset: 0, background: 'rgba(7,5,10,0.72)' }} />
                      </div>
                    )}

                    {/* 背景番号 */}
                    <div style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', fontSize: '90px', fontWeight: 700, color: 'rgba(201,169,97,0.04)', lineHeight: 1, userSelect: 'none', pointerEvents: 'none', fontFamily: 'var(--font-cinzel)', zIndex: 1, ...(isRight ? { right: '12px' } : { left: '12px' }) }}>
                      {f.num}
                    </div>

                    <div style={{ position: 'relative', zIndex: 2, padding: '28px 24px', display: 'flex', flexDirection: 'column', ...(isRight ? { alignItems: 'flex-end', textAlign: 'right' } : { alignItems: 'flex-start', textAlign: 'left' }) }}>

                      {/* ENラベル＋番号 */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px', ...(isRight ? { flexDirection: 'row-reverse' } : {}) }}>
                        <span style={{ fontSize: '9px', letterSpacing: '0.5em', color: GOLD_DIM, textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>{f.en}</span>
                        <div style={{ width: '16px', height: '1px', backgroundColor: 'rgba(201,169,97,0.3)' }} />
                        <span style={{ fontSize: '9px', color: 'rgba(201,169,97,0.35)', fontFamily: 'var(--font-cinzel)' }}>{f.num}</span>
                      </div>

                      {/* タイトル */}
                      <h3 style={{ display: 'inline-block', fontSize: '20px', fontWeight: 700, color: GOLD_BRIGHT, lineHeight: 1.2, marginBottom: '8px', letterSpacing: '0.05em', border: `1px solid rgba(201,169,97,0.5)`, padding: '4px 12px', backgroundColor: 'rgba(201,169,97,0.05)' }}>
                        {f.title}
                      </h3>

                      {/* キャッチコピー */}
                      <p style={{ fontSize: '11px', color: CREAM_DIM, lineHeight: '24px', whiteSpace: 'pre-line', letterSpacing: '0.05em' }}>
                        {f.catch}
                      </p>

                      {/* 矢印 */}
                      <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', ...(isRight ? { flexDirection: 'row-reverse' } : {}) }}>
                        <div style={{ width: '24px', height: '1px', backgroundColor: 'rgba(201,169,97,0.4)' }} />
                        <span style={{ fontSize: '10px', color: GOLD_DIM, fontFamily: 'var(--font-cinzel)' }}>{isRight ? '←' : '→'}</span>
                      </div>
                    </div>

                    {/* アクセントライン */}
                    <div style={{ position: 'absolute', top: 0, bottom: 0, width: '2px', zIndex: 3, background: 'linear-gradient(to bottom, transparent, rgba(201,169,97,0.4), transparent)', ...(isRight ? { right: 0 } : { left: 0 }) }} />
                  </div>
                </Link>

                {/* ブリッジテキスト */}
                {f.bridge && (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '16px 32px' }}>
                    <div style={{ width: '1px', height: '16px', background: 'linear-gradient(to bottom, rgba(201,169,97,0.3), rgba(201,169,97,0.15))' }} />
                    <p style={{ textAlign: 'center', fontSize: '10px', color: CREAM_FAINT, letterSpacing: '0.1em', lineHeight: '20px', padding: '8px 16px', borderLeft: `1px solid rgba(201,169,97,0.1)`, borderRight: `1px solid rgba(201,169,97,0.1)` }}>
                      {f.bridge}
                    </p>
                    <div style={{ width: '1px', height: '16px', background: 'linear-gradient(to bottom, rgba(201,169,97,0.15), rgba(201,169,97,0.3))' }} />
                    <div style={{ fontSize: '8px', color: 'rgba(201,169,97,0.4)' }}>▼</div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div style={{ textAlign: 'center', paddingBottom: '40px' }}>
          <div style={{ height: '1px', background: 'linear-gradient(to right, transparent, rgba(201,169,97,0.15), transparent)', marginBottom: '24px' }} />
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: 'rgba(245,239,224,0.2)', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>© 2026 Group Yggdrasill</p>
        </div>
      </section>
    </main>
  );
}
