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
type PlanItem = { id: string; label: string; price: number; note?: string };
type SeatType = {
  id: string;
  label: string;
  desc: string;
  plans: PlanItem[];
};

const SEATS: SeatType[] = [
  {
    id: 'main',
    label: 'Main Floor',
    desc: 'メインフロア',
    plans: [
      { id: 'quick',     label: 'クイック（60分・時間制限）', price: 10000, note: 'スラット・淡麗・お茶割り・JJ茉莉花のいずれか2セット無料。3セット目以降、またはそれ以外のドリンクは別途料金。60分でチェックアウト。' },
      { id: 'normal',    label: '通常（フリータイム）',       price: 21000, note: 'ドリンクは別途。閉店まで滞在可能。' },
      { id: 'nomi_main', label: '飲み放題（90分）',           price: 30000, note: '一部ドリンクは別途。延長¥15,000 / 60分。' },
    ],
  },
  {
    id: 'vip_sofa',
    label: 'V.I.P.Sofa',
    desc: 'VIPソファ席',
    plans: [
      { id: 'vip_sofa_normal', label: '通常（フリータイム）', price: 30000, note: 'ドリンクは別途。' },
      { id: 'nomi_vip',        label: '飲み放題（90分）',     price: 50000, note: '一部ドリンクは別途。延長¥25,000 / 60分。' },
    ],
  },
  {
    id: 'vip_box',
    label: 'V.I.P.Box',
    desc: 'VIPボックス席',
    plans: [
      { id: 'vip_box_normal', label: '通常（フリータイム）', price: 35000, note: 'ドリンクは別途。' },
      { id: 'nomi_vip',       label: '飲み放題（90分）',     price: 50000, note: '一部ドリンクは別途。延長¥25,000 / 60分。' },
    ],
  },
  {
    id: 'exe',
    label: 'Executive Room',
    desc: 'エグゼクティブルーム',
    plans: [
      { id: 'exe_normal', label: '通常（フリータイム）', price: 50000,  note: 'ドリンクは別途。' },
      { id: 'nomi_exe',   label: '飲み放題（90分）',    price: 100000, note: '一部ドリンクは別途。延長¥50,000 / 60分。' },
    ],
  },
];

// 延長料金（飲み放題選択時のみ表示）
const EXT_PLANS: Record<string, PlanItem> = {
  main:     { id: 'nomi_ext',     label: '延長（+60分）', price: 15000 },
  vip_sofa: { id: 'nomi_vip_ext', label: '延長（+60分）', price: 25000 },
  vip_box:  { id: 'nomi_vip_ext', label: '延長（+60分）', price: 25000 },
  exe:      { id: 'nomi_exe_ext', label: '延長（+60分）', price: 50000 },
};

// ===================== ドリンクメニュー =====================
type DrinkItem = { id: string; name: string; base: number; variants?: { label: string; base: number }[] };
type DrinkCategory = { cat: string; items: DrinkItem[] };

const DRINKS: DrinkCategory[] = [
  {
    cat: 'ノンアルコールドリンク',
    items: [
      { id: 'soft_1k', name: '緑茶／烏龍茶／麦茶／コーン茶／ジャスミン茶／ストレートティー／レモンティー／ミルクティー／オレンジジュース／アップルジュース／グレープフルーツジュース／パインジュース／グレープジュース／アセロラジュース／カルピス', base: 1000 },
      { id: 'soft_2k', name: 'コーラ／ジンジャエール／ラムネ／クラブソーダ／トマトジュース／ネクター／ポカリスエット', base: 2000 },
      { id: 'redbull_na', name: 'レッドブル', base: 3000 },
      { id: 'perrier', name: 'ペリエ', base: 6000 },
      { id: 'junzo', name: '順造選（りんご／白桃／マンゴー／ブルーベリー／みかん／パイナップル）', base: 8000 },
    ],
  },
  {
    cat: 'アルコールドリンク',
    items: [
      { id: 'beer',     name: '瓶ビール',    base: 3000 },
      { id: 'ochawari', name: 'お茶割り',    base: 3000 },
      { id: 'tanrei',   name: '淡麗',        base: 3000 },
      { id: 'slat',     name: 'スラット',    base: 3000 },
      { id: 'jj',       name: 'JJ茉莉花',   base: 3000 },
      { id: 'otoko',    name: '男梅',        base: 4000 },
      { id: 'hyoketsu', name: '氷結',        base: 4000 },
      { id: 'highball', name: 'ハイボール',  base: 5000 },
      { id: 'rbv',      name: 'レッドブルウォッカ', base: 6000 },
      { id: 'pokav',    name: 'ポカリウォッカ',     base: 6000 },
    ],
  },
  {
    cat: 'ショットグラス',
    items: [
      { id: 'jager',      name: 'イエガー',       base: 4000 },
      { id: 'cocarelo',   name: 'コカレロ',       base: 4000 },
      { id: 'tarantula',  name: 'タランチュラ',   base: 4000 },
      { id: 'tequila_b',  name: 'テキーラボール', base: 4000 },
      { id: 'tequila_r',  name: 'テキーラローズ', base: 4000 },
      { id: 'anejo',      name: 'アネホテキーラ', base: 5000 },
      { id: 'cocapom',    name: 'コカポム',       base: 5000 },
      { id: 'kleiner',    name: 'クライナー',     base: 5000 },
      { id: 'habu',       name: 'ハブ酒',         base: 5000 },
      { id: 'vodka',      name: 'ウォッカ',       base: 6000 },
      { id: 'cristalino', name: 'クリスタリーノ', base: 9000 },
      { id: 'tequila_car',  name: 'テキーラ観覧車',        base: 70000 },
      { id: 'aneho_car',    name: 'アネホ観覧車',           base: 100000 },
      { id: 'tequila_globe','name': 'テキーラ地球儀',       base: 100000 },
      { id: 'tequila_ship', name: 'テキーラシップ',         base: 130000 },
      { id: 'cristal_car',  name: 'クリスタリーノ観覧車',   base: 150000 },
      { id: 'aneho_globe',  name: 'アネホ地球儀',           base: 150000 },
    ],
  },
  {
    cat: 'シャンパン',
    items: [
      { id: 'cafe_paris',  name: 'カフェドパリ',            base: 15000 },
      { id: 'asti',        name: 'アスティ',                base: 45000 },
      { id: 'vuv_yellow',  name: 'ヴーヴ・グリコ イエロー', base: 70000 },
      { id: 'tobeg',       name: 'TO BE G',                 base: 80000 },
      { id: 'vuv_white',   name: 'ヴーヴ・グリコ ホワイト', base: 80000 },
      {
        id: 'moet',
        name: 'モエ・エ・シャンドン',
        base: 90000,
        variants: [
          { label: 'ホワイト',        base: 90000  },
          { label: 'ロゼ',            base: 140000 },
          { label: 'ネクター ブラック', base: 150000 },
        ],
      },
      {
        id: 'roger',
        name: 'ロジャーグラード',
        base: 100000,
        variants: [
          { label: 'ロゼ',   base: 100000 },
          { label: 'ゴールド', base: 150000 },
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
      { id: 'mapam', name: 'マパム・グラシア', base: 120000 },
    ],
  },
  {
    cat: 'フード',
    items: [
      { id: 'potage',      name: 'ポタージュ',                                           base: 2000 },
      { id: 'chips',       name: 'ポテトチップス（ソルト／トリュフ／チーズ／ハニー／ガーリック）', base: 2000 },
      { id: 'gelato',      name: 'ジェラート（バニラ／ストロベリー／抹茶／チョコレート）', base: 3000 },
      { id: 'sandwich',    name: 'サンドイッチ（ミックス／ハム卵／ツナ）',               base: 3000 },
      { id: 'waffle',      name: 'ワッフルサンド（クリームチーズ＆生ハム）',             base: 3000 },
      { id: 'honey_lemon', name: 'はちみつレモン',                                       base: 3000 },
      { id: 'smoothie_s',  name: 'スムージー (S)',                                       base: 3000 },
      { id: 'smoothie_l',  name: 'スムージー (L)',                                       base: 5000 },
    ],
  },
];

function fmt(n: number) {
  return '¥' + n.toLocaleString('ja-JP');
}

type CartItem = { id: string; name: string; base: number; price: number; qty: number };

export default function SimulatorPage() {
  const [seatId, setSeatId] = useState<string>('');
  const [planId, setPlanId] = useState<string>('');
  const [extQty, setExtQty] = useState<number>(0);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [openCat, setOpenCat] = useState<string>('');

  const selectedSeat = SEATS.find(s => s.id === seatId);
  const selectedPlan = selectedSeat?.plans.find(p => p.id === planId);
  const isNomi = planId.startsWith('nomi_');
  const extPlan = seatId ? EXT_PLANS[seatId] : null;
  const setPrice = (selectedPlan?.price ?? 0) + (isNomi && extPlan ? extPlan.price * extQty : 0);
  const drinkTotal = cart.reduce((sum, c) => sum + c.price * c.qty, 0);
  const total = setPrice + drinkTotal;

  function getQty(id: string, name: string) {
    return cart.find(c => c.id === id && c.name === name)?.qty ?? 0;
  }

  function addItem(id: string, name: string, basePrice: number) {
    const price = calc(basePrice);
    setCart(prev => {
      const existing = prev.find(c => c.id === id && c.name === name);
      if (existing) return prev.map(c => c.id === id && c.name === name ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { id, name, base: basePrice, price, qty: 1 }];
    });
  }

  function removeItem(id: string, name: string) {
    setCart(prev => prev.flatMap(c => {
      if (c.id !== id || c.name !== name) return [c];
      if (c.qty > 1) return [{ ...c, qty: c.qty - 1 }];
      return [];
    }));
  }

  const divider = <div style={{ height: '1px', background: 'linear-gradient(to right, transparent, rgba(201,169,97,0.2), transparent)' }} />;

  // カウンターUI（各ドリンク行に表示）
  function Counter({ id, name, base }: { id: string; name: string; base: number }) {
    const qty = getQty(id, name);
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
        {qty > 0 && (
          <button onClick={(e) => { e.stopPropagation(); removeItem(id, name); }}
            style={{ width: '26px', height: '26px', border: '1px solid rgba(201,169,97,0.35)', background: 'transparent', color: GOLD_DIM, fontSize: '15px', cursor: 'pointer', borderRadius: '50%', lineHeight: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            −
          </button>
        )}
        {qty > 0 && (
          <span style={{ fontSize: '14px', fontWeight: 700, color: GOLD_BRIGHT, minWidth: '16px', textAlign: 'center' }}>{qty}</span>
        )}
        <button onClick={(e) => { e.stopPropagation(); addItem(id, name, base); }}
          style={{ width: '26px', height: '26px', border: `1px solid ${qty > 0 ? GOLD : 'rgba(201,169,97,0.35)'}`, background: qty > 0 ? 'rgba(201,169,97,0.15)' : 'transparent', color: qty > 0 ? GOLD_BRIGHT : GOLD_DIM, fontSize: '15px', cursor: 'pointer', borderRadius: '50%', lineHeight: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          ＋
        </button>
      </div>
    );
  }

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
            席・プランを選んでドリンクの個数を入力すると合計金額の目安がわかります。
          </p>
        </section>

        {divider}

        {/* STEP 1 席を選ぶ */}
        <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '6px', fontFamily: 'var(--font-cinzel)' }}>
            Step 01 — 席を選ぶ
          </p>
          <p style={{ fontSize: '11px', color: CREAM_DIM, marginBottom: '14px' }}>どのエリアに座りますか？</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {SEATS.map(seat => {
              const active = seatId === seat.id;
              return (
                <button
                  key={seat.id}
                  onClick={() => { setSeatId(active ? '' : seat.id); setPlanId(''); setExtQty(0); }}
                  style={{
                    textAlign: 'left', padding: '14px 14px',
                    border: active ? `1px solid ${GOLD}` : '1px solid rgba(201,169,97,0.2)',
                    background: active ? 'rgba(201,169,97,0.12)' : 'rgba(255,255,255,0.02)',
                    cursor: 'pointer', borderRadius: '4px',
                  }}
                >
                  <p style={{ fontSize: '13px', fontWeight: 700, color: active ? GOLD_BRIGHT : CREAM, margin: '0 0 3px' }}>{seat.label}</p>
                  <p style={{ fontSize: '10px', color: CREAM_DIM, margin: 0 }}>{seat.desc}</p>
                </button>
              );
            })}
          </div>
        </section>

        {/* STEP 3 プランを選ぶ（席選択後に表示） */}
        {selectedSeat && (
          <>
            {divider}
            <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
              <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '6px', fontFamily: 'var(--font-cinzel)' }}>
                Step 02 — プランを選ぶ
              </p>
              <p style={{ fontSize: '11px', color: CREAM_DIM, marginBottom: '14px' }}>
                <span style={{ color: GOLD_BRIGHT, fontWeight: 700 }}>{selectedSeat.label}</span> でのプランを選んでください。
              </p>
              <div style={{ display: 'grid', gap: '8px' }}>
                {selectedSeat.plans.map(plan => {
                  const active = planId === plan.id;
                  return (
                    <button
                      key={plan.id}
                      onClick={() => { setPlanId(active ? '' : plan.id); setExtQty(0); }}
                      style={{
                        width: '100%', textAlign: 'left', padding: '14px 16px',
                        border: active ? `1px solid ${GOLD}` : '1px solid rgba(201,169,97,0.2)',
                        background: active ? 'rgba(201,169,97,0.1)' : 'rgba(255,255,255,0.02)',
                        cursor: 'pointer', borderRadius: '4px',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: '14px', fontWeight: 700, color: active ? GOLD_BRIGHT : CREAM, margin: '0 0 3px' }}>{plan.label}</p>
                        {plan.note && <p style={{ fontSize: '11px', color: 'rgba(245,239,224,0.45)', margin: 0, lineHeight: '18px' }}>{plan.note}</p>}
                      </div>
                      <p style={{ fontSize: '16px', fontWeight: 700, color: active ? GOLD_BRIGHT : GOLD_DIM, whiteSpace: 'nowrap', marginLeft: '16px' }}>
                        {fmt(plan.price)}
                      </p>
                    </button>
                  );
                })}
              </div>

              {/* 飲み放題の延長オプション */}
              {isNomi && extPlan && (
                <div style={{ marginTop: '14px', padding: '14px 16px', border: '1px solid rgba(201,169,97,0.15)', borderRadius: '4px', background: 'rgba(255,255,255,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <p style={{ fontSize: '13px', color: CREAM, margin: '0 0 2px', fontWeight: 600 }}>{extPlan.label}</p>
                      <p style={{ fontSize: '11px', color: CREAM_DIM, margin: 0 }}>{fmt(extPlan.price)} / 60分</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <button onClick={() => setExtQty(q => Math.max(0, q - 1))} style={{ width: '30px', height: '30px', border: '1px solid rgba(201,169,97,0.3)', background: 'transparent', color: GOLD_DIM, fontSize: '16px', cursor: 'pointer', borderRadius: '50%' }}>−</button>
                      <span style={{ fontSize: '16px', fontWeight: 700, color: extQty > 0 ? GOLD_BRIGHT : 'rgba(245,239,224,0.4)', minWidth: '20px', textAlign: 'center' }}>{extQty}</span>
                      <button onClick={() => setExtQty(q => q + 1)} style={{ width: '30px', height: '30px', border: '1px solid rgba(201,169,97,0.3)', background: 'transparent', color: GOLD_DIM, fontSize: '16px', cursor: 'pointer', borderRadius: '50%' }}>＋</button>
                    </div>
                  </div>
                </div>
              )}

              {/* クイック選択時の無料ドリンク案内 */}
              {planId === 'quick' && (
                <div style={{ marginTop: '14px', padding: '12px 14px', background: 'rgba(100,200,150,0.07)', border: '1px solid rgba(100,200,150,0.25)', borderRadius: '4px' }}>
                  <p style={{ fontSize: '11px', color: 'rgba(100,220,160,0.9)', fontWeight: 700, margin: '0 0 6px' }}>✓ 無料で付く2セット（缶物）</p>
                  <p style={{ fontSize: '12px', color: CREAM_DIM, margin: 0, lineHeight: '20px' }}>
                    スラット・淡麗・お茶割り・JJ茉莉花 のいずれか
                  </p>
                  <p style={{ fontSize: '10px', color: 'rgba(245,239,224,0.35)', margin: '6px 0 0', lineHeight: '18px' }}>
                    ※3セット目以降、またはそれ以外のドリンクを追加した場合は下の「ドリンク追加」から選んで料金に加算してください。
                  </p>
                </div>
              )}

              <p style={{ fontSize: '10px', color: 'rgba(245,239,224,0.3)', marginTop: '10px', lineHeight: '18px' }}>
                ※セット料金は税・サービス料込みの金額です。
              </p>
            </section>
          </>
        )}

        {divider}

        {/* STEP 3 ドリンク選択（席＋プラン選択後のみ） */}
        <section style={{ paddingTop: '24px', paddingBottom: '24px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '6px', fontFamily: 'var(--font-cinzel)' }}>
            Step 03 — ドリンク・フードを選ぶ
          </p>

          {/* 未選択時のロック表示 */}
          {!selectedPlan ? (
            <div style={{ padding: '24px 16px', border: '1px dashed rgba(201,169,97,0.2)', borderRadius: '4px', textAlign: 'center' }}>
              <p style={{ fontSize: '20px', margin: '0 0 8px' }}>🔒</p>
              <p style={{ fontSize: '12px', color: 'rgba(245,239,224,0.4)', margin: 0, lineHeight: '20px' }}>
                Step 01・02 で席とプランを<br />選択するとドリンクを追加できます
              </p>
            </div>
          ) : (
            <>
          <p style={{ fontSize: '10px', color: 'rgba(201,169,97,0.6)', marginBottom: '16px', lineHeight: '18px' }}>
            価格はメニュー表記。全て消費税10%・サービス料35%となります（合計欄に反映）
          </p>
          <div style={{ display: 'grid', gap: '6px' }}>
            {DRINKS.map(cat => {
              const isOpen = openCat === cat.cat;
              const catTotal = cat.items.reduce((sum, item) => {
                if (item.variants) {
                  return sum + item.variants.reduce((s, v) => s + (getQty(`${item.id}_${v.label}`, `${item.name} ${v.label}`) * v.base), 0);
                }
                return sum + getQty(item.id, item.name) * item.base;
              }, 0);
              return (
                <div key={cat.cat} style={{ border: '1px solid rgba(201,169,97,0.15)', borderRadius: '4px', overflow: 'hidden' }}>
                  <button
                    onClick={() => setOpenCat(isOpen ? '' : cat.cat)}
                    style={{
                      width: '100%', textAlign: 'left', padding: '12px 16px',
                      background: isOpen ? 'rgba(201,169,97,0.07)' : 'rgba(255,255,255,0.02)',
                      border: 'none', cursor: 'pointer',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}
                  >
                    <span style={{ fontSize: '13px', fontWeight: 600, color: isOpen ? GOLD_BRIGHT : CREAM }}>{cat.cat}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {catTotal > 0 && <span style={{ fontSize: '11px', color: GOLD_BRIGHT, fontWeight: 700 }}>{fmt(catTotal)}</span>}
                      <span style={{ fontSize: '10px', color: GOLD_DIM }}>{isOpen ? '▲' : '▼'}</span>
                    </div>
                  </button>
                  {isOpen && (
                    <div style={{ borderTop: '1px solid rgba(201,169,97,0.1)' }}>
                      {cat.items.map(item => {
                        if (item.variants) {
                          return (
                            <div key={item.id} style={{ borderBottom: '1px solid rgba(201,169,97,0.08)' }}>
                              <div style={{ padding: '8px 16px 4px' }}>
                                <span style={{ fontSize: '11px', color: 'rgba(245,239,224,0.5)', fontWeight: 600 }}>{item.name}</span>
                              </div>
                              {item.variants.map(v => {
                                const vid = `${item.id}_${v.label}`;
                                const vname = `${item.name} ${v.label}`;
                                return (
                                  <div key={v.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 16px 8px 24px', borderTop: '1px solid rgba(201,169,97,0.05)' }}>
                                    <div>
                                      <span style={{ fontSize: '12px', color: CREAM }}>{v.label}</span>
                                      <span style={{ fontSize: '11px', color: GOLD_DIM, marginLeft: '8px' }}>{fmt(v.base)}</span>
                                    </div>
                                    <Counter id={vid} name={vname} base={v.base} />
                                  </div>
                                );
                              })}
                            </div>
                          );
                        }
                        return (
                          <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', borderBottom: '1px solid rgba(201,169,97,0.08)' }}>
                            <div style={{ flex: 1, marginRight: '12px' }}>
                              <p style={{ fontSize: '12px', color: CREAM, margin: 0 }}>{item.name}</p>
                              <p style={{ fontSize: '11px', color: GOLD_DIM, margin: '2px 0 0' }}>{fmt(item.base)}</p>
                            </div>
                            <Counter id={item.id} name={item.name} base={item.base} />
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
            </>
          )}
        </section>

        {divider}

        {/* 合計 */}
        <section style={{ paddingTop: '28px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD, textTransform: 'uppercase', marginBottom: '16px', fontFamily: 'var(--font-cinzel)' }}>
            Result
          </p>

          <div style={{ border: 'rgba(201,169,97,0.35) solid 1px', borderRadius: '4px', padding: '20px', background: 'linear-gradient(135deg, rgba(201,169,97,0.08), rgba(7,5,10,0.6))' }}>

            {/* セット料金 */}
            {selectedSeat && selectedPlan && (
              <div style={{ marginBottom: '14px' }}>
                <p style={{ fontSize: '9px', letterSpacing: '0.3em', color: GOLD_DIM, margin: '0 0 6px', textTransform: 'uppercase' }}>セット料金（税・サービス料込み）</p>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '12px', color: CREAM_DIM }}>{selectedSeat.label}　{selectedPlan.label}</span>
                  <span style={{ fontSize: '12px', color: CREAM }}>{fmt(selectedPlan.price)}</span>
                </div>
                {isNomi && extPlan && extQty > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                    <span style={{ fontSize: '12px', color: CREAM_DIM }}>延長 ×{extQty}</span>
                    <span style={{ fontSize: '12px', color: CREAM }}>{fmt(extPlan.price * extQty)}</span>
                  </div>
                )}
              </div>
            )}

            {/* ドリンク明細 */}
            {cart.length > 0 && (() => {
              const baseSum = cart.reduce((s, c) => s + c.base * c.qty, 0);
              const taxService = drinkTotal - baseSum;
              return (
                <div style={{ marginBottom: '14px' }}>
                  <p style={{ fontSize: '9px', letterSpacing: '0.3em', color: GOLD_DIM, margin: '0 0 6px', textTransform: 'uppercase' }}>ドリンク明細</p>
                  {cart.map(c => (
                    <div key={c.id + c.name} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                      <span style={{ fontSize: '12px', color: CREAM_DIM, flex: 1, marginRight: '8px' }}>{c.name}</span>
                      <span style={{ fontSize: '11px', color: 'rgba(245,239,224,0.4)', marginRight: '8px' }}>{fmt(c.base)} × {c.qty}</span>
                      <span style={{ fontSize: '12px', color: CREAM, minWidth: '64px', textAlign: 'right' }}>{fmt(c.base * c.qty)}</span>
                    </div>
                  ))}
                  <div style={{ borderTop: '1px solid rgba(201,169,97,0.12)', marginTop: '8px', paddingTop: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                      <span style={{ fontSize: '11px', color: 'rgba(245,239,224,0.4)' }}>小計</span>
                      <span style={{ fontSize: '11px', color: 'rgba(245,239,224,0.4)' }}>{fmt(baseSum)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                      <span style={{ fontSize: '11px', color: 'rgba(201,169,97,0.5)' }}>消費税10% + サービス料35%</span>
                      <span style={{ fontSize: '11px', color: 'rgba(201,169,97,0.5)' }}>+{fmt(taxService)}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '12px', color: CREAM_DIM, fontWeight: 600 }}>ドリンク合計</span>
                      <span style={{ fontSize: '12px', color: CREAM, fontWeight: 600 }}>{fmt(drinkTotal)}</span>
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* 最終合計 */}
            <div style={{ height: '1px', background: 'rgba(201,169,97,0.3)', margin: '4px 0 14px' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', letterSpacing: '0.1em', color: GOLD, fontFamily: 'var(--font-cinzel)' }}>合計目安</span>
              <span style={{ fontSize: '30px', fontWeight: 700, color: GOLD_BRIGHT, fontFamily: 'var(--font-display)' }}>
                {fmt(total)}
              </span>
            </div>
          </div>

          <p style={{ fontSize: '10px', color: 'rgba(245,239,224,0.3)', marginTop: '12px', lineHeight: '18px' }}>
            ※ドリンク価格はメニュー表記の金額に消費税10%・サービス料35%を加算し、¥1,000未満切り上げで計算しています。<br />
            ※セット料金はすでに税・サービス料込みの金額です。<br />
            ※実際の料金はお店の状況によって異なる場合があります。
          </p>

          {(seatId || cart.length > 0) && (
            <button
              onClick={() => { setSeatId(''); setPlanId(''); setExtQty(0); setCart([]); }}
              style={{ marginTop: '20px', width: '100%', padding: '12px', border: '1px solid rgba(201,169,97,0.2)', background: 'transparent', color: GOLD_DIM, fontSize: '12px', cursor: 'pointer', letterSpacing: '0.1em', borderRadius: '4px' }}
            >
              リセット
            </button>
          )}
        </section>

      </div>
    </main>
  );
}
