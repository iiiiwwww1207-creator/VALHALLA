'use client';

import { useState } from 'react';
import Link from 'next/link';

const GOLD = '#C9A961';
const GOLD_BRIGHT = '#E8CB85';
const GOLD_DIM = 'rgba(201,169,97,0.5)';
const CREAM = '#F5EFE0';
const CREAM_DIM = 'rgba(245,239,224,0.55)';
const DARK = '#07050A';

// ¥1,000未満切り上げ
function calc(base: number) {
  return Math.ceil((base * 1.35 * 1.1) / 1000) * 1000;
}

// ===================== セット料金 =====================
type SetItem = {
  id: string;
  label: string;
  sub: string;
  price: number;
  note?: string;
  tag?: string;
};

type SetGroup = { group: string; items: SetItem[] };

const SET_GROUPS: SetGroup[] = [
  {
    group: 'Main Floor',
    items: [
      {
        id: 'quick',
        label: 'クイック',
        sub: '60分・時間制限制',
        price: 10000,
        note: '缶物2本込み。60分でチェックアウト。',
        tag: '時間制限',
      },
      {
        id: 'normal',
        label: '通常',
        sub: 'フリータイム',
        price: 21000,
        note: 'ドリンクは別途。閉店まで滞在可能。',
        tag: 'フリータイム',
      },
      {
        id: 'nomi_main',
        label: '飲み放題',
        sub: '90分',
        price: 30000,
        note: '一部ドリンクは別途。延長は60分ごとに¥15,000。',
        tag: '90分',
      },
    ],
  },
  {
    group: '飲み放題 延長',
    items: [
      {
        id: 'nomi_ext',
        label: '延長料金',
        sub: '60分ごと',
        price: 15000,
        note: '飲み放題の延長料金（60分単位）。',
      },
    ],
  },
  {
    group: 'V.I.P Floor',
    items: [
      {
        id: 'vip_sofa',
        label: 'V.I.P.Sofa',
        sub: 'フリータイム',
        price: 30000,
        note: 'ドリンクは別途。',
      },
      {
        id: 'vip_box',
        label: 'V.I.P.Box',
        sub: 'フリータイム',
        price: 35000,
        note: 'ドリンクは別途。',
      },
      {
        id: 'nomi_vip',
        label: 'VIP飲み放題',
        sub: '90分',
        price: 50000,
        note: '一部ドリンクは別途。',
      },
      {
        id: 'nomi_vip_ext',
        label: 'VIP延長',
        sub: '60分ごと',
        price: 25000,
      },
    ],
  },
  {
    group: 'Executive Room',
    items: [
      {
        id: 'exe',
        label: 'Executive Room',
        sub: 'フリータイム',
        price: 50000,
        note: 'ドリンクは別途。',
      },
      {
        id: 'nomi_exe',
        label: 'Executive飲み放題',
        sub: '90分',
        price: 100000,
        note: '一部ドリンクは別途。',
      },
      {
        id: 'nomi_exe_ext',
        label: 'Executive延長',
        sub: '60分ごと',
        price: 50000,
      },
    ],
  },
  {
    group: 'その他',
    items: [
      {
        id: 'jonai_set',
        label: '場内指名',
        sub: '税・サービス料別',
        price: 1000,
      },
      {
        id: 'dohan_set',
        label: '同伴料金',
        sub: '税・サービス料別',
        price: 3000,
      },
    ],
  },
];

// ===================== ドリンクメニュー =====================
type DrinkItem = { id: string; name: string; base: number; variants?: { label: string; base: number }[] };
type DrinkCategory = { cat: string; items: DrinkItem[] };

const DRINKS: DrinkCategory[] = [
  {
    cat: 'ノンアルコール',
    items: [
      { id: 'soft_1k', name: '緑茶・烏龍茶・各種ソフト', base: 1000 },
      { id: 'soft_2k', name: 'コーラ・ラムネ・ポカリ等', base: 2000 },
      { id: 'redbull_na', name: 'レッドブル', base: 3000 },
      { id: 'perrier', name: 'ペリエ', base: 6000 },
      { id: 'junzo', name: '順造選（果実ジュース）', base: 8000 },
    ],
  },
  {
    cat: 'アルコール',
    items: [
      { id: 'beer', name: '瓶ビール／お茶割り／淡麗／スラット／JJ茉莉花', base: 3000 },
      { id: 'otoko', name: '男梅／氷結', base: 4000 },
      { id: 'highball', name: 'ハイボール', base: 5000 },
      { id: 'rbv', name: 'レッドブルウォッカ／ポカリウォッカ', base: 6000 },
    ],
  },
  {
    cat: 'ショットグラス',
    items: [
      { id: 'shot_4k', name: 'イエガー／コカレロ／タランチュラ／テキーラ系', base: 4000 },
      { id: 'shot_5k', name: 'アネホテキーラ／コカポム／クライナー／ハブ酒', base: 5000 },
      { id: 'shot_vodka', name: 'ウォッカ', base: 6000 },
      { id: 'shot_cristal', name: 'クリスタリーノ', base: 9000 },
      { id: 'tequila_car', name: 'テキーラ観覧車', base: 70000 },
      { id: 'aneho_car', name: 'アネホ観覧車', base: 100000 },
      { id: 'cristal_car', name: 'クリスタリーノ観覧車', base: 150000 },
      { id: 'tequila_globe', name: 'テキーラ地球儀', base: 100000 },
      { id: 'aneho_globe', name: 'アネホ地球儀', base: 150000 },
      { id: 'tequila_ship', name: 'テキーラシップ', base: 130000 },
    ],
  },
  {
    cat: 'ボトル（焼酎・梅酒）',
    items: [
      { id: 'ginkotake', name: '銀高謙／銀高梅酒', base: 12000 },
      { id: 'japan', name: 'JAPAN／黒霧島', base: 15000 },
      { id: 'umeshu_ex', name: '梅酒エクセレント', base: 18000 },
      { id: 'yuzu', name: '柚子小町', base: 20000 },
      { id: 'kichiroku', name: '吉四六', base: 80000 },
    ],
  },
  {
    cat: 'ワイン',
    items: [
      { id: 'chablis', name: 'ルイ ラトゥール シャブリ（白）', base: 120000 },
      { id: 'sixeight', name: 'シックスエイト（赤）', base: 120000 },
    ],
  },
  {
    cat: 'ブランデー',
    items: [
      { id: 'remy_vsop', name: 'レミーマルタン VSOP', base: 100000 },
    ],
  },
  {
    cat: 'ウイスキー',
    items: [
      { id: 'laphroig', name: 'ラフロイグ 10年', base: 100000 },
      { id: 'macallan', name: 'ザ マッカラン 12年', base: 150000 },
    ],
  },
  {
    cat: 'ノンアルコールシャンパン',
    items: [
      { id: 'shamai_rose', name: 'シャメイロゼ', base: 100000 },
      { id: 'shamai_gold', name: 'シャメイゴールド', base: 150000 },
    ],
  },
  {
    cat: 'シャンパン I',
    items: [
      { id: 'cafe_paris', name: 'カフェドパリ', base: 15000 },
      { id: 'asti', name: 'アスティ', base: 45000 },
      { id: 'tobeg', name: 'TO BE G', base: 80000 },
      { id: 'mapam', name: 'マパム・グラシア', base: 120000 },
      { id: 'vuv_yellow', name: 'ヴーヴ・グリコ イエロー', base: 70000 },
      { id: 'vuv_white', name: 'ヴーヴ・グリコ ホワイト', base: 80000 },
      {
        id: 'roger',
        name: 'ロジャーグラード',
        base: 100000,
        variants: [
          { label: 'ロゼ', base: 100000 },
          { label: 'ゴールド', base: 150000 },
        ],
      },
      {
        id: 'moet',
        name: 'モエ・エ・シャンドン',
        base: 90000,
        variants: [
          { label: 'ホワイト', base: 90000 },
          { label: 'ロゼ', base: 140000 },
          { label: 'ネクター ブラック', base: 150000 },
        ],
      },
      {
        id: 'ygd_orig',
        name: 'YGGDRASILLオリジナル',
        base: 100000,
        variants: [
          { label: '¥100,000', base: 100000 },
          { label: '¥150,000', base: 150000 },
        ],
      },
    ],
  },
  {
    cat: 'フード',
    items: [
      { id: 'gelato', name: 'ジェラート', base: 3000 },
      { id: 'potage', name: 'ポタージュ', base: 2000 },
      { id: 'sandwich', name: 'サンドイッチ', base: 3000 },
      { id: 'waffle', name: 'ワッフルサンド', base: 3000 },
      { id: 'honey_lemon', name: 'はちみつレモン', base: 3000 },
      { id: 'smoothie_s', name: 'スムージー (S)', base: 3000 },
      { id: 'smoothie_l', name: 'スムージー (L)', base: 5000 },
      { id: 'chips', name: 'ポテトチップス', base: 2000 },
    ],
  },
  {
    cat: 'その他チャージ',
    items: [
      { id: 'jonai', name: '場内指名', base: 1000 },
      { id: 'dohan', name: '同伴料金', base: 3000 },
    ],
  },
];

function fmt(n: number) {
  return '¥' + n.toLocaleString('ja-JP');
}

type CartItem = { id: string; name: string; price: number; qty: number };

export default function SimulatorPage() {
  const [setId, setSetId] = useState<string>('');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [openCat, setOpenCat] = useState<string>('');
  const [variantOpen, setVariantOpen] = useState<string>('');

  const allSets = SET_GROUPS.flatMap(g => g.items);
  const selectedSet = allSets.find(s => s.id === setId);
  const setPrice = selectedSet ? selectedSet.price : 0;

  const drinkTotal = cart.reduce((sum, c) => sum + c.price * c.qty, 0);
  const total = setPrice + drinkTotal;

  function addDrinkDirect(id: string, name: string, basePrice: number) {
    const price = calc(basePrice);
    setCart(prev => {
      const existing = prev.find(c => c.id === id && c.name === name);
      if (existing) return prev.map(c => c.id === id && c.name === name ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { id, name, price, qty: 1 }];
    });
  }

  function removeItem(id: string, name: string) {
    setCart(prev => prev.flatMap(c => {
      if (c.id !== id || c.name !== name) return [c];
      if (c.qty > 1) return [{ ...c, qty: c.qty - 1 }];
      return [];
    }));
  }

  const divider = <div style={{ height: '1px', background: 'linear-gradient(to right, transparent, rgba(201,169,97,0.2), transparent)', margin: '0' }} />;

  return (
    <main style={{ minHeight: '100dvh', backgroundColor: DARK, color: CREAM, fontFamily: 'var(--font-body)', overflowX: 'hidden' }}>
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(201,169,97,0.07) 0%, transparent 60%)' }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '480px', margin: '0 auto', padding: '0 20px 80px' }}>

        {/* ヘッダー */}
        <div style={{ paddingTop: '32px', paddingBottom: '8px' }}>
          <Link href="/" style={{ color: GOLD_DIM, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}>
            ← 戻る
          </Link>
        </div>

        {/* タイトル */}
        <section style={{ paddingTop: '16px', paddingBottom: '28px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.5em', color: GOLD_DIM, textTransform: 'uppercase', marginBottom: '8px', fontFamily: 'var(--font-cinzel)' }}>Price Simulator</p>
          <h1 style={{ fontSize: '28px', fontWeight: 700, color: GOLD_BRIGHT, fontFamily: 'var(--font-display)', lineHeight: 1.2, marginBottom: '10px' }}>
            料金シミュレーター
          </h1>
          <p style={{ fontSize: '12px', color: CREAM_DIM, lineHeight: '22px' }}>
            セット料金＋ドリンクを選んで合計金額の目安を確認できます。
          </p>
        </section>

        {divider}

        {/* STEP 1 セット選択 */}
        <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '6px', fontFamily: 'var(--font-cinzel)' }}>
            Step 01 — セット料金
          </p>
          <p style={{ fontSize: '11px', color: CREAM_DIM, marginBottom: '18px', lineHeight: '20px' }}>
            料金形態を1つ選んでください。
          </p>

          {/* 料金形態3種（Main Floor）を目立たせる */}
          <div style={{ display: 'grid', gap: '10px', marginBottom: '20px' }}>
            {SET_GROUPS[0].items.map(s => {
              const active = setId === s.id;
              const tagColors: Record<string, string> = {
                '時間制限': 'rgba(255,100,100,0.8)',
                'フリータイム': 'rgba(100,200,150,0.8)',
                '90分': 'rgba(100,160,255,0.8)',
              };
              return (
                <button
                  key={s.id}
                  onClick={() => setSetId(active ? '' : s.id)}
                  style={{
                    width: '100%', textAlign: 'left', padding: '16px 16px',
                    border: active ? `1px solid ${GOLD}` : '1px solid rgba(201,169,97,0.25)',
                    background: active ? 'rgba(201,169,97,0.1)' : 'rgba(255,255,255,0.03)',
                    cursor: 'pointer', borderRadius: '4px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <p style={{ fontSize: '15px', fontWeight: 700, color: active ? GOLD_BRIGHT : CREAM, margin: 0 }}>{s.label}</p>
                        {s.tag && (
                          <span style={{ fontSize: '9px', padding: '2px 7px', borderRadius: '20px', border: `1px solid ${tagColors[s.tag] ?? GOLD_DIM}`, color: tagColors[s.tag] ?? GOLD_DIM }}>
                            {s.tag}
                          </span>
                        )}
                      </div>
                      {s.note && <p style={{ fontSize: '11px', color: 'rgba(245,239,224,0.45)', margin: 0, lineHeight: '18px' }}>{s.note}</p>}
                    </div>
                    <p style={{ fontSize: '16px', fontWeight: 700, color: active ? GOLD_BRIGHT : GOLD_DIM, whiteSpace: 'nowrap', marginLeft: '14px' }}>
                      {fmt(s.price)}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>

          {/* その他のセット（折りたたみ） */}
          {SET_GROUPS.slice(1).map(g => {
            const isOpen = openCat === g.group;
            return (
              <div key={g.group} style={{ border: '1px solid rgba(201,169,97,0.12)', borderRadius: '4px', overflow: 'hidden', marginBottom: '6px' }}>
                <button
                  onClick={() => setOpenCat(isOpen ? '' : g.group)}
                  style={{
                    width: '100%', textAlign: 'left', padding: '11px 16px',
                    background: isOpen ? 'rgba(201,169,97,0.06)' : 'rgba(255,255,255,0.02)',
                    border: 'none', cursor: 'pointer',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  }}
                >
                  <span style={{ fontSize: '12px', color: isOpen ? GOLD_BRIGHT : 'rgba(245,239,224,0.7)', fontWeight: 600 }}>{g.group}</span>
                  <span style={{ fontSize: '10px', color: GOLD_DIM }}>{isOpen ? '▲' : '▼'}</span>
                </button>
                {isOpen && (
                  <div style={{ borderTop: '1px solid rgba(201,169,97,0.1)' }}>
                    {g.items.map(s => {
                      const active = setId === s.id;
                      return (
                        <button
                          key={s.id}
                          onClick={() => setSetId(active ? '' : s.id)}
                          style={{
                            width: '100%', textAlign: 'left', padding: '11px 16px',
                            background: active ? 'rgba(201,169,97,0.08)' : 'transparent',
                            border: 'none', borderBottom: '1px solid rgba(201,169,97,0.07)',
                            cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          }}
                        >
                          <div>
                            <p style={{ fontSize: '13px', fontWeight: 600, color: active ? GOLD_BRIGHT : CREAM, margin: 0 }}>{s.label}</p>
                            <p style={{ fontSize: '11px', color: CREAM_DIM, margin: '2px 0 0' }}>{s.sub}</p>
                          </div>
                          <p style={{ fontSize: '13px', fontWeight: 700, color: active ? GOLD_BRIGHT : GOLD_DIM, whiteSpace: 'nowrap', marginLeft: '12px' }}>
                            {fmt(s.price)}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}

          <p style={{ fontSize: '10px', color: 'rgba(245,239,224,0.3)', marginTop: '10px', lineHeight: '18px' }}>
            ※セット料金は税・サービス料込みの金額です。
          </p>
        </section>

        {divider}

        {/* STEP 2 ドリンク選択 */}
        <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '14px', fontFamily: 'var(--font-cinzel)' }}>
            Step 02 — ドリンク・フード
          </p>
          <p style={{ fontSize: '11px', color: CREAM_DIM, marginBottom: '16px', lineHeight: '20px' }}>
            カテゴリをタップして追加できます。表示価格はすべて税・サービス料込みの目安金額です。
          </p>
          <div style={{ display: 'grid', gap: '6px' }}>
            {DRINKS.map(cat => {
              const isOpen = openCat === cat.cat;
              return (
                <div key={cat.cat} style={{ border: '1px solid rgba(201,169,97,0.15)', borderRadius: '4px', overflow: 'hidden' }}>
                  <button
                    onClick={() => setOpenCat(isOpen ? '' : cat.cat)}
                    style={{
                      width: '100%', textAlign: 'left', padding: '12px 16px',
                      background: isOpen ? 'rgba(201,169,97,0.07)' : 'rgba(255,255,255,0.02)',
                      border: 'none', cursor: 'pointer', color: isOpen ? GOLD_BRIGHT : CREAM,
                      fontSize: '13px', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}
                  >
                    <span>{cat.cat}</span>
                    <span style={{ fontSize: '10px', color: GOLD_DIM }}>{isOpen ? '▲' : '▼'}</span>
                  </button>
                  {isOpen && (
                    <div style={{ borderTop: '1px solid rgba(201,169,97,0.1)' }}>
                      {cat.items.map(item => {
                        const isVarOpen = variantOpen === item.id;
                        const displayPrice = calc(item.base);

                        if (item.variants) {
                          return (
                            <div key={item.id} style={{ borderBottom: '1px solid rgba(201,169,97,0.08)' }}>
                              <button
                                onClick={() => setVariantOpen(isVarOpen ? '' : item.id)}
                                style={{
                                  width: '100%', textAlign: 'left', padding: '10px 16px',
                                  background: isVarOpen ? 'rgba(201,169,97,0.05)' : 'transparent',
                                  border: 'none', cursor: 'pointer',
                                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                }}
                              >
                                <span style={{ fontSize: '12px', color: CREAM }}>{item.name}</span>
                                <span style={{ fontSize: '10px', color: GOLD_DIM }}>種類を選ぶ ▶</span>
                              </button>
                              {isVarOpen && (
                                <div style={{ background: 'rgba(201,169,97,0.04)', padding: '4px 0' }}>
                                  {item.variants!.map(v => (
                                    <button
                                      key={v.label}
                                      onClick={() => addDrinkDirect(`${item.id}_${v.label}`, `${item.name} ${v.label}`, v.base)}
                                      style={{
                                        width: '100%', textAlign: 'left', padding: '8px 24px',
                                        background: 'transparent', border: 'none', cursor: 'pointer',
                                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                      }}
                                    >
                                      <span style={{ fontSize: '12px', color: 'rgba(245,239,224,0.8)' }}>{v.label}</span>
                                      <span style={{ fontSize: '12px', color: GOLD_BRIGHT, fontWeight: 600 }}>
                                        {fmt(calc(v.base))}
                                      </span>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        }

                        return (
                          <button
                            key={item.id}
                            onClick={() => addDrinkDirect(item.id, item.name, item.base)}
                            style={{
                              width: '100%', textAlign: 'left', padding: '10px 16px',
                              background: 'transparent', border: 'none', borderBottom: '1px solid rgba(201,169,97,0.08)',
                              cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            }}
                          >
                            <span style={{ fontSize: '12px', color: CREAM, flex: 1, marginRight: '8px' }}>{item.name}</span>
                            <span style={{ fontSize: '13px', color: GOLD_BRIGHT, fontWeight: 600, whiteSpace: 'nowrap' }}>
                              + {fmt(displayPrice)}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {divider}

        {/* カート */}
        {cart.length > 0 && (
          <>
            <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
              <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '14px', fontFamily: 'var(--font-cinzel)' }}>
                Selected Items
              </p>
              <div style={{ display: 'grid', gap: '6px' }}>
                {cart.map(c => (
                  <div key={c.id + c.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', border: '1px solid rgba(201,169,97,0.15)', borderRadius: '4px', background: 'rgba(201,169,97,0.04)' }}>
                    <div style={{ flex: 1, marginRight: '8px' }}>
                      <p style={{ fontSize: '12px', color: CREAM, margin: 0 }}>{c.name}</p>
                      <p style={{ fontSize: '11px', color: GOLD_DIM, margin: '2px 0 0' }}>{fmt(c.price)} × {c.qty}</p>
                    </div>
                    <p style={{ fontSize: '13px', fontWeight: 700, color: GOLD_BRIGHT, marginRight: '12px', whiteSpace: 'nowrap' }}>
                      {fmt(c.price * c.qty)}
                    </p>
                    <button
                      onClick={() => removeItem(c.id, c.name)}
                      style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(201,169,97,0.2)', color: GOLD_DIM, width: '28px', height: '28px', borderRadius: '50%', cursor: 'pointer', fontSize: '14px', flexShrink: 0 }}
                    >
                      −
                    </button>
                  </div>
                ))}
              </div>
            </section>
            {divider}
          </>
        )}

        {/* 合計 */}
        <section style={{ paddingTop: '28px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '16px', fontFamily: 'var(--font-cinzel)' }}>
            Total
          </p>
          <div style={{ border: `1px solid rgba(201,169,97,0.35)`, borderRadius: '4px', padding: '20px', background: 'linear-gradient(135deg, rgba(201,169,97,0.08), rgba(7,5,10,0.6))' }}>
            {selectedSet && (
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ fontSize: '12px', color: CREAM_DIM }}>{selectedSet.label}</span>
                <span style={{ fontSize: '12px', color: CREAM }}>{fmt(setPrice)}</span>
              </div>
            )}
            {cart.length > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span style={{ fontSize: '12px', color: CREAM_DIM }}>ドリンク合計</span>
                <span style={{ fontSize: '12px', color: CREAM }}>{fmt(drinkTotal)}</span>
              </div>
            )}
            <div style={{ height: '1px', background: 'rgba(201,169,97,0.2)', margin: '12px 0' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', letterSpacing: '0.1em', color: GOLD, fontFamily: 'var(--font-cinzel)' }}>合計目安</span>
              <span style={{ fontSize: '26px', fontWeight: 700, color: GOLD_BRIGHT, fontFamily: 'var(--font-display)' }}>
                {fmt(total)}
              </span>
            </div>
          </div>
          <p style={{ fontSize: '10px', color: 'rgba(245,239,224,0.3)', marginTop: '12px', lineHeight: '18px' }}>
            ※ドリンク価格は定価×消費税10%×サービス料35%の目安金額です（¥1,000未満切り上げ）。<br />
            ※セット料金はすでに税・サービス料込みの金額です。<br />
            ※実際の料金はお店の状況によって異なる場合があります。
          </p>

          {/* リセット */}
          {(setId || cart.length > 0) && (
            <button
              onClick={() => { setSetId(''); setCart([]); }}
              style={{
                marginTop: '20px', width: '100%', padding: '12px',
                border: '1px solid rgba(201,169,97,0.2)', background: 'transparent',
                color: GOLD_DIM, fontSize: '12px', cursor: 'pointer', letterSpacing: '0.1em',
                borderRadius: '4px',
              }}
            >
              リセット
            </button>
          )}
        </section>

      </div>
    </main>
  );
}
