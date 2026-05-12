'use client';

// ============================================================
// 相性診断ページ
//
// 【仕様（確定）】
//   - 診断結果に表示するキャストは VALHALLA の76名のみ
//   - データソース: src/data/cast-public.ts（誕生日なし・公開用）
//   - cast-list.ts（誕生日あり）はこのファイルで絶対にimportしない
//
// 【アルゴリズムについて】
//   - マッチングロジック（compatScore関数）は後日別担当者が実装予定
//   - 現在は仮実装（数秘術ベース）が入っている
//   - 実装時は CAST_PUBLIC の lifePathNumber（1〜9）を使うこと
//   - キャストの誕生日には触れない設計
// ============================================================

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { CAST_PUBLIC, type CastPublic } from '../../src/data/cast-public';

// ── カラー定数 ──────────────────────────────────────────
const GOLD = '#C9A961';
const GOLD_BRIGHT = '#E8CB85';
const CREAM = '#F5EFE0';
const CREAM_DIM = 'rgba(245,239,224,0.55)';
const CREAM_FAINT = 'rgba(245,239,224,0.35)';
const GOLD_DIM = 'rgba(201,169,97,0.5)';
const DARK = '#07050A';

// ── 数秘術：ライフパスナンバー計算 ────────────────────────
function reduceToSingle(n: number): number {
  while (n > 9) {
    n = String(n).split('').reduce((s, d) => s + Number(d), 0);
  }
  return n || 9;
}

function calcLifePath(year: number, month: number, day: number): number {
  const sum = `${year}${month}${day}`
    .split('')
    .reduce((s, d) => s + Number(d), 0);
  return reduceToSingle(sum);
}

// ── キャストのオーラナンバー（インデックスベースで 1〜9）──
function castAura(index: number): number {
  return (index % 9) + 1;
}

// ── 相性スコアテーブル（数秘術の相性）────────────────────
// compatibility[a-1][b-1] = 0〜100
const COMPAT: number[][] = [
  // 1   2   3   4   5   6   7   8   9
  [100, 55, 85, 40, 90, 70, 75, 65, 60], // 1
  [ 55,100, 60, 90, 50, 95, 70, 80, 75], // 2
  [ 85, 60,100, 45, 80, 65, 90, 55, 70], // 3
  [ 40, 90, 45,100, 55, 85, 60, 95, 65], // 4
  [ 90, 50, 80, 55,100, 60, 85, 70, 75], // 5
  [ 70, 95, 65, 85, 60,100, 55, 90, 80], // 6
  [ 75, 70, 90, 60, 85, 55,100, 65, 95], // 7
  [ 65, 80, 55, 95, 70, 90, 65,100, 60], // 8
  [ 60, 75, 70, 65, 75, 80, 95, 60,100], // 9
];

function compatScore(myNum: number, castIdx: number): number {
  const aura = castAura(castIdx);
  return COMPAT[myNum - 1][aura - 1];
}

// ── 相性メッセージ ────────────────────────────────────────
function compatMessage(score: number): string {
  if (score >= 95) return '魂が共鳴する運命の出会い';
  if (score >= 85) return '深い縁で結ばれた特別な相手';
  if (score >= 75) return '自然と心が通じ合う関係';
  if (score >= 65) return '互いを高め合えるバランス';
  return '新鮮な出会いが刺激をくれる';
}

// ── ライフパスナンバーの説明 ──────────────────────────────
const LP_DESC: Record<number, string> = {
  1: '独立心が強く、自分の道を切り開くリーダー気質',
  2: '繊細で共感力が高く、深い絆を大切にする調和の人',
  3: '創造性と表現力にあふれ、周囲に喜びをもたらす',
  4: '誠実で信頼感があり、コツコツと積み上げる堅実派',
  5: '自由を愛し好奇心旺盛、変化を楽しむ冒険者',
  6: '責任感が強く愛情深い、人を包み込む癒しの存在',
  7: '直感と知性を兼ね備えた、神秘的な探求者',
  8: '強い意志と実行力で夢を現実にする達成の人',
  9: '博愛的で慈悲深く、人々を導く智慧の持ち主',
};

// ── ドラムロールピッカー ──────────────────────────────────
const ITEM_H = 48; // 1行の高さ(px)

function DrumPicker({ items, value, onChange, label }: {
  items: string[];
  value: string;
  onChange: (v: string) => void;
  label: string;
}) {
  const listRef = React.useRef<HTMLDivElement>(null);
  const idx = items.indexOf(value);

  // 選択中インデックスへスクロール
  React.useEffect(() => {
    if (!listRef.current) return;
    const target = (idx < 0 ? 0 : idx) * ITEM_H;
    listRef.current.scrollTo({ top: target, behavior: 'smooth' });
  }, [idx]);

  function onScroll() {
    if (!listRef.current) return;
    const i = Math.round(listRef.current.scrollTop / ITEM_H);
    const clamped = Math.max(0, Math.min(items.length - 1, i));
    if (items[clamped] !== value) onChange(items[clamped]);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
      <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: GOLD_DIM, textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)', marginBottom: '8px' }}>{label}</p>
      <div style={{ position: 'relative', width: '100%' }}>
        {/* 上下フェード */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: `${ITEM_H}px`, background: `linear-gradient(to bottom, rgba(7,5,10,0.95), transparent)`, zIndex: 2, pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: `${ITEM_H}px`, background: `linear-gradient(to top, rgba(7,5,10,0.95), transparent)`, zIndex: 2, pointerEvents: 'none' }} />
        {/* 選択枠 */}
        <div style={{ position: 'absolute', top: `${ITEM_H}px`, left: 0, right: 0, height: `${ITEM_H}px`, border: '1px solid rgba(201,169,97,0.5)', background: 'rgba(201,169,97,0.06)', zIndex: 1, pointerEvents: 'none' }} />
        {/* スクロール領域 */}
        <div
          ref={listRef}
          onScroll={onScroll}
          style={{
            height: `${ITEM_H * 3}px`,
            overflowY: 'scroll',
            scrollSnapType: 'y mandatory',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
          }}
        >
          {/* 上パディング */}
          <div style={{ height: `${ITEM_H}px` }} />
          {items.map(item => (
            <div
              key={item}
              onClick={() => onChange(item)}
              style={{
                height: `${ITEM_H}px`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                scrollSnapAlign: 'center',
                fontSize: item === value ? '22px' : '16px',
                fontWeight: item === value ? 700 : 400,
                color: item === value ? GOLD_BRIGHT : 'rgba(245,239,224,0.3)',
                fontFamily: 'var(--font-cinzel)',
                letterSpacing: '0.05em',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {item}
            </div>
          ))}
          {/* 下パディング */}
          <div style={{ height: `${ITEM_H}px` }} />
        </div>
      </div>
    </div>
  );
}

// ── コンポーネント ────────────────────────────────────────
type Step = 'input' | 'result';

const YEARS  = Array.from({ length: 2010 - 1980 + 1 }, (_, i) => String(1980 + i));
const MONTHS = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, '0'));
const DAYS   = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'));

export default function MatchingPage() {
  const [year, setYear] = useState('1995');
  const [month, setMonth] = useState('01');
  const [day, setDay] = useState('01');
  const [step, setStep] = useState<Step>('input');
  const [results, setResults] = useState<{ cast: CastPublic; score: number; rank: number }[]>([]);
  const [lifePathNum, setLifePathNum] = useState(0);
  const [revealed, setRevealed] = useState<number[]>([]);

  const isValid = Number(year) >= 1980 && Number(year) <= 2010
    && Number(month) >= 1 && Number(month) <= 12
    && Number(day) >= 1 && Number(day) <= 31;

  function handleDiagnose() {
    const lp = calcLifePath(Number(year), Number(month), Number(day));
    setLifePathNum(lp);

    const scored = CAST_PUBLIC.map((c, i) => ({
      cast: c,
      score: compatScore(lp, i),
      rank: i,
    }));
    scored.sort((a, b) => b.score - a.score || a.rank - b.rank);
    setResults(scored.slice(0, 5));
    setRevealed([]);
    setStep('result');
  }

  function handleReveal(index: number) {
    setRevealed(prev => prev.includes(index) ? prev : [...prev, index]);
  }

  function handleReset() {
    setStep('input');
    setYear('');
    setMonth('');
    setDay('');
    setRevealed([]);
  }

  // GitHub Pages では /VALHALLA/ プレフィックスが必要
  const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? '';
  // 写真ありのキャストだけ抽出してシャッフル
  const photoList = CAST_PUBLIC.filter(c => c.image).map(c => `${BASE}${c.image}`);
  // 3行分のリスト（各行に使う写真を少しずつずらす）
  const row1 = [...photoList.slice(0, 24), ...photoList.slice(0, 24)];
  const row2 = [...photoList.slice(12, 36), ...photoList.slice(12, 36)];
  const row3 = [...photoList.slice(24), ...photoList.slice(24)];

  return (
    <main style={{ minHeight: '100dvh', backgroundColor: DARK, color: CREAM, overflowX: 'hidden', fontFamily: 'var(--font-body)' }}>

      {/* ── CSS アニメーション定義 ── */}
      <style>{`
        @keyframes marquee-left {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes marquee-right {
          0%   { transform: translateX(-50%); }
          100% { transform: translateX(0); }
        }
        .marquee-left  { animation: marquee-left  40s linear infinite; }
        .marquee-right { animation: marquee-right 50s linear infinite; }
        .marquee-left2 { animation: marquee-left  60s linear infinite; }
      `}</style>

      {/* 背景グロー */}
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0, background: 'radial-gradient(ellipse at 50% 0%, rgba(201,169,97,0.06) 0%, transparent 60%)' }} />

      <div style={{ position: 'relative', zIndex: 10, maxWidth: '480px', margin: '0 auto', padding: '0 20px 60px' }}>

        {/* ── 戻るボタン ── */}
        <div style={{ paddingTop: '32px', paddingBottom: '16px' }}>
          <Link href="/" style={{ color: GOLD_DIM, fontSize: '13px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px', letterSpacing: '0.05em' }}>
            ← 戻る
          </Link>
        </div>

        {/* ── ヘッダー（写真流れる背景付き）── */}
        <div style={{ position: 'relative', textAlign: 'center', paddingTop: '48px', paddingBottom: '48px', overflow: 'hidden', margin: '0 -20px' }}>

          {/* 流れる写真 3行 */}
          <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', gap: '3px', pointerEvents: 'none' }}>
            {/* 1行目: 左へ */}
            <div style={{ display: 'flex', gap: '3px', overflow: 'hidden', flex: 1 }}>
              <div className="marquee-left" style={{ display: 'flex', gap: '3px', flexShrink: 0 }}>
                {row1.map((img, i) => (
                  <img key={i} src={img} alt="" loading="eager" style={{ width: '72px', flexShrink: 0, height: '100%', objectFit: 'cover', objectPosition: 'center 15%', display: 'block' }} />
                ))}
              </div>
            </div>
            {/* 2行目: 右へ */}
            <div style={{ display: 'flex', gap: '3px', overflow: 'hidden', flex: 1 }}>
              <div className="marquee-right" style={{ display: 'flex', gap: '3px', flexShrink: 0 }}>
                {row2.map((img, i) => (
                  <img key={i} src={img} alt="" loading="eager" style={{ width: '72px', flexShrink: 0, height: '100%', objectFit: 'cover', objectPosition: 'center 15%', display: 'block' }} />
                ))}
              </div>
            </div>
            {/* 3行目: 左へ（速度違う） */}
            <div style={{ display: 'flex', gap: '3px', overflow: 'hidden', flex: 1 }}>
              <div className="marquee-left2" style={{ display: 'flex', gap: '3px', flexShrink: 0 }}>
                {row3.map((img, i) => (
                  <img key={i} src={img} alt="" loading="eager" style={{ width: '72px', flexShrink: 0, height: '100%', objectFit: 'cover', objectPosition: 'center 15%', display: 'block' }} />
                ))}
              </div>
            </div>
          </div>

          {/* 全体に薄暗いオーバーレイ */}
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(7,5,10,0.55)', pointerEvents: 'none' }} />
          {/* 上下グラデーション（端をなじませる） */}
          <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(to bottom, ${DARK} 0%, transparent 20%, transparent 80%, ${DARK} 100%)`, pointerEvents: 'none' }} />
          {/* テキスト中央部だけさらに暗くして読みやすく */}
          <div style={{ position: 'absolute', left: 0, right: 0, top: '30%', bottom: '30%', background: 'rgba(7,5,10,0.4)', pointerEvents: 'none' }} />

          {/* テキスト */}
          <div style={{ position: 'relative', zIndex: 2 }}>
            <p style={{ fontSize: '9px', letterSpacing: '0.6em', color: GOLD, marginBottom: '12px', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>Compatibility</p>
            <h1 style={{ fontSize: '28px', fontWeight: 700, color: GOLD_BRIGHT, fontFamily: 'var(--font-cinzel)', letterSpacing: '0.1em', marginBottom: '12px', textShadow: '0 0 30px rgba(0,0,0,1), 0 2px 8px rgba(0,0,0,0.9)' }}>
              相性診断
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', justifyContent: 'center' }}>
              <div style={{ height: '1px', width: '40px', backgroundColor: 'rgba(201,169,97,0.3)' }} />
              <span style={{ fontSize: '11px', color: CREAM_FAINT, letterSpacing: '0.15em' }}>数秘術であなたの運命を読み解く</span>
              <div style={{ height: '1px', width: '40px', backgroundColor: 'rgba(201,169,97,0.3)' }} />
            </div>
          </div>
        </div>

        {step === 'input' && (
          <InputSection
            year={year} month={month} day={day}
            setYear={setYear} setMonth={setMonth} setDay={setDay}
            isValid={isValid}
            onDiagnose={handleDiagnose}
          />
        )}

        {step === 'result' && (
          <ResultSection
            lifePathNum={lifePathNum}
            results={results}
            revealed={revealed}
            onReveal={handleReveal}
            onReset={handleReset}
          />
        )}
      </div>
    </main>
  );
}

// ── 入力セクション ─────────────────────────────────────────
function InputSection({
  year, month, day, setYear, setMonth, setDay, isValid, onDiagnose
}: {
  year: string; month: string; day: string;
  setYear: (v: string) => void;
  setMonth: (v: string) => void;
  setDay: (v: string) => void;
  isValid: boolean;
  onDiagnose: () => void;
}) {
  return (
    <div>
      {/* 説明文 */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <p style={{ fontSize: '12px', color: CREAM_DIM, lineHeight: '28px', letterSpacing: '0.05em' }}>
          生年月日を選択してください<br />
          数秘術があなたにとって<br />
          <span style={{ color: GOLD_BRIGHT }}>最も相性の良いキャスト</span>を導き出します
        </p>
      </div>

      {/* ドラムロールピッカー */}
      <div style={{ border: '1px solid rgba(201,169,97,0.25)', padding: '24px 16px 32px', marginBottom: '32px', background: 'linear-gradient(160deg, rgba(255,255,255,0.02), rgba(26,15,34,0.6))' }}>
        <p style={{ fontSize: '9px', letterSpacing: '0.5em', color: GOLD_DIM, textTransform: 'uppercase', marginBottom: '20px', textAlign: 'center', fontFamily: 'var(--font-cinzel)' }}>Birth Date</p>
        <style>{`
          div::-webkit-scrollbar { display: none; }
        `}</style>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
          <DrumPicker items={YEARS}  value={year}  onChange={setYear}  label="Year" />
          <div style={{ paddingTop: '68px', color: 'rgba(201,169,97,0.4)', fontSize: '18px', flexShrink: 0 }}>/</div>
          <DrumPicker items={MONTHS} value={month} onChange={setMonth} label="Month" />
          <div style={{ paddingTop: '68px', color: 'rgba(201,169,97,0.4)', fontSize: '18px', flexShrink: 0 }}>/</div>
          <DrumPicker items={DAYS}   value={day}   onChange={setDay}   label="Day" />
        </div>
        {/* 選択中の日付表示 */}
        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '11px', color: 'rgba(201,169,97,0.5)', letterSpacing: '0.2em', fontFamily: 'var(--font-cinzel)' }}>
          {year} / {month} / {day}
        </p>
      </div>

      {/* 診断ボタン */}
      <button
        onClick={onDiagnose}
        disabled={!isValid}
        style={{
          width: '100%',
          padding: '18px',
          background: isValid
            ? 'linear-gradient(135deg, rgba(201,169,97,0.25), rgba(232,203,133,0.15))'
            : 'rgba(201,169,97,0.05)',
          border: `1px solid ${isValid ? 'rgba(201,169,97,0.7)' : 'rgba(201,169,97,0.2)'}`,
          color: isValid ? GOLD_BRIGHT : 'rgba(201,169,97,0.3)',
          fontSize: '13px',
          letterSpacing: '0.4em',
          cursor: isValid ? 'pointer' : 'not-allowed',
          fontFamily: 'var(--font-cinzel)',
          transition: 'all 0.2s ease',
        }}
      >
        DIAGNOSE
      </button>

      {/* 注記 */}
      <p style={{ textAlign: 'center', fontSize: '10px', color: 'rgba(245,239,224,0.2)', marginTop: '20px', letterSpacing: '0.05em' }}>
        ※ 数秘術はエンターテインメント目的です
      </p>
    </div>
  );
}

// ── 結果セクション ─────────────────────────────────────────
function ResultSection({
  lifePathNum, results, revealed, onReveal, onReset
}: {
  lifePathNum: number;
  results: { cast: CastPublic; score: number; rank: number }[];
  revealed: number[];
  onReveal: (i: number) => void;
  onReset: () => void;
}) {
  const top3 = results.slice(0, 3);
  const rest = results.slice(3);

  return (
    <div>
      {/* ライフパスナンバー表示 */}
      <div style={{ textAlign: 'center', marginBottom: '40px', padding: '28px 24px', border: '1px solid rgba(201,169,97,0.2)', background: 'linear-gradient(160deg, rgba(201,169,97,0.06), rgba(7,5,10,0.8))' }}>
        <p style={{ fontSize: '9px', letterSpacing: '0.5em', color: GOLD_DIM, marginBottom: '12px', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>Your Life Path Number</p>
        <div style={{ fontSize: '72px', fontWeight: 700, color: GOLD_BRIGHT, fontFamily: 'var(--font-cinzel)', lineHeight: 1, marginBottom: '16px', textShadow: '0 0 30px rgba(201,169,97,0.3)' }}>
          {lifePathNum}
        </div>
        <p style={{ fontSize: '11px', color: CREAM_DIM, lineHeight: '22px', letterSpacing: '0.05em' }}>
          {LP_DESC[lifePathNum]}
        </p>
      </div>

      {/* TOP 3 */}
      <div style={{ marginBottom: '12px' }}>
        <p style={{ fontSize: '9px', letterSpacing: '0.5em', color: GOLD_DIM, textTransform: 'uppercase', marginBottom: '20px', textAlign: 'center', fontFamily: 'var(--font-cinzel)' }}>
          Your Top Matches
        </p>

        {top3.map((r, i) => (
          <CastCard
            key={r.cast.id}
            entry={r}
            rank={i + 1}
            isRevealed={revealed.includes(i)}
            onReveal={() => onReveal(i)}
          />
        ))}
      </div>

      {/* その他 2名 */}
      {rest.length > 0 && (
        <div style={{ marginBottom: '32px' }}>
          <p style={{ fontSize: '9px', letterSpacing: '0.4em', color: 'rgba(201,169,97,0.3)', textAlign: 'center', marginBottom: '12px', textTransform: 'uppercase', fontFamily: 'var(--font-cinzel)' }}>
            Also Compatible
          </p>
          {rest.map((r, i) => (
            <div
              key={r.cast.id}
              style={{
                display: 'flex', alignItems: 'center', gap: '12px',
                padding: '12px 16px',
                borderTop: '1px solid rgba(201,169,97,0.08)',
              }}
            >
              <span style={{ fontSize: '9px', color: 'rgba(201,169,97,0.3)', fontFamily: 'var(--font-cinzel)', minWidth: '20px' }}>0{i + 4}</span>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', overflow: 'hidden', border: '1px solid rgba(201,169,97,0.2)', flexShrink: 0 }}>
                <Image src={r.cast.image} alt={r.cast.name} width={40} height={40} style={{ objectFit: 'cover', width: '100%', height: '100%' }} />
              </div>
              <span style={{ fontSize: '13px', color: CREAM_DIM, flex: 1 }}>{r.cast.name}</span>
              <span style={{ fontSize: '12px', color: GOLD, fontFamily: 'var(--font-cinzel)' }}>{r.score}%</span>
            </div>
          ))}
        </div>
      )}

      {/* もう一度ボタン */}
      <button
        onClick={onReset}
        style={{
          width: '100%', padding: '16px',
          background: 'transparent',
          border: '1px solid rgba(201,169,97,0.35)',
          color: GOLD_DIM, fontSize: '12px',
          letterSpacing: '0.4em', cursor: 'pointer',
          fontFamily: 'var(--font-cinzel)',
        }}
      >
        RETRY
      </button>
    </div>
  );
}

// ── キャストカード ─────────────────────────────────────────
function CastCard({
  entry, rank, isRevealed, onReveal,
}: {
  entry: { cast: CastPublic; score: number };
  rank: number;
  isRevealed: boolean;
  onReveal: () => void;
}) {
  const { cast, score } = entry;
  const medals = ['✦', '✧', '◇'];

  return (
    <div
      style={{
        position: 'relative', marginBottom: '16px', overflow: 'hidden',
        border: rank === 1 ? '1px solid rgba(201,169,97,0.5)' : '1px solid rgba(201,169,97,0.2)',
        background: rank === 1
          ? 'linear-gradient(160deg, rgba(201,169,97,0.08), rgba(7,5,10,0.9))'
          : 'linear-gradient(160deg, rgba(255,255,255,0.02), rgba(7,5,10,0.8))',
      }}
    >
      {/* ランクバッジ */}
      <div style={{
        position: 'absolute', top: 0, left: 0,
        padding: '4px 10px',
        background: rank === 1 ? 'rgba(201,169,97,0.2)' : 'rgba(201,169,97,0.08)',
        borderRight: '1px solid rgba(201,169,97,0.2)',
        borderBottom: '1px solid rgba(201,169,97,0.2)',
        fontSize: '9px', color: GOLD, fontFamily: 'var(--font-cinzel)', letterSpacing: '0.3em',
      }}>
        {medals[rank - 1]} {String(rank).padStart(2, '0')}
      </div>

      {/* 写真エリア */}
      <div style={{ display: 'flex', padding: '32px 20px 20px' }}>
        <div style={{
          width: '90px', height: '110px', flexShrink: 0,
          position: 'relative', overflow: 'hidden',
          border: '1px solid rgba(201,169,97,0.3)',
        }}>
          {/* ぼかし → タップで表示 */}
          <Image
            src={cast.image}
            alt={cast.name}
            fill
            style={{
              objectFit: 'cover',
              filter: isRevealed ? 'none' : 'blur(12px) brightness(0.6)',
              transition: 'filter 0.5s ease',
            }}
          />
          {!isRevealed && (
            <button
              onClick={onReveal}
              style={{
                position: 'absolute', inset: 0, display: 'flex',
                flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                background: 'transparent', border: 'none', cursor: 'pointer',
                gap: '4px',
              }}
            >
              <span style={{ fontSize: '18px' }}>👁</span>
              <span style={{ fontSize: '8px', color: GOLD, letterSpacing: '0.2em', fontFamily: 'var(--font-cinzel)' }}>REVEAL</span>
            </button>
          )}
        </div>

        {/* テキスト */}
        <div style={{ flex: 1, paddingLeft: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <p style={{ fontSize: '16px', fontWeight: 700, color: rank === 1 ? GOLD_BRIGHT : CREAM, marginBottom: '4px', letterSpacing: '0.05em' }}>
              {cast.name}
            </p>
          </div>

          {/* 相性スコア */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '9px', color: GOLD_DIM, letterSpacing: '0.3em', fontFamily: 'var(--font-cinzel)' }}>COMPATIBILITY</span>
              <span style={{ fontSize: '14px', color: GOLD_BRIGHT, fontFamily: 'var(--font-cinzel)', fontWeight: 700 }}>{score}%</span>
            </div>
            {/* バー */}
            <div style={{ height: '3px', background: 'rgba(201,169,97,0.15)', position: 'relative', overflow: 'hidden' }}>
              <div style={{
                position: 'absolute', left: 0, top: 0, bottom: 0,
                width: `${score}%`,
                background: score >= 90
                  ? 'linear-gradient(to right, #C9A961, #E8CB85)'
                  : 'linear-gradient(to right, rgba(201,169,97,0.6), rgba(201,169,97,0.4))',
              }} />
            </div>
          </div>

          <p style={{ fontSize: '10px', color: CREAM_FAINT, lineHeight: '18px', letterSpacing: '0.05em', marginTop: '8px' }}>
            {compatMessage(score)}
          </p>
        </div>
      </div>
    </div>
  );
}
