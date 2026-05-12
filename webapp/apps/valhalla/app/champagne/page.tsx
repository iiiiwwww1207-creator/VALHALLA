'use client';
import Link from 'next/link';

export default function Page() {
  return (
    <main className="min-h-dvh bg-[#070509] text-[#F5EFE0]" style={{ fontFamily: 'var(--font-body)' }}>
      <div className="fixed inset-0 pointer-events-none z-0" style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(201,169,97,0.08) 0%, transparent 60%)' }} />
      <div className="relative z-10 max-w-[480px] mx-auto px-5 pb-10">
        <div className="pt-8 pb-4">
          <Link href="/" className="text-[rgba(201,169,97,0.7)] text-sm flex items-center gap-1">← 戻る</Link>
        </div>
        <div className="text-center py-12">
          <p className="text-[10px] tracking-[0.5em] text-[#C9A961] mb-4 uppercase" style={{ fontFamily: 'var(--font-cinzel)' }}>CHAMPAGNE CALL</p>
          <div className="text-5xl mb-6">🍾</div>
          <h1 className="text-2xl font-bold text-[#E8CB85] mb-4" style={{ fontFamily: 'var(--font-cinzel)' }}>シャンパンコール動画</h1>
          <p className="text-sm text-[rgba(245,239,224,0.55)] leading-7 whitespace-pre-line">実際のシャンパンコールを\n体感してみよう</p>
        </div>
        <div className="rounded-2xl border border-[rgba(201,169,97,0.2)] p-8 text-center" style={{ background: 'linear-gradient(160deg, rgba(255,255,255,0.03), rgba(26,15,34,0.8))' }}>
          <p className="text-[#C9A961] text-sm tracking-widest" style={{ fontFamily: 'var(--font-cinzel)' }}>Coming Soon</p>
          <p className="text-xs text-[rgba(245,239,224,0.4)] mt-2">実装中です</p>
        </div>
      </div>
    </main>
  );
}
