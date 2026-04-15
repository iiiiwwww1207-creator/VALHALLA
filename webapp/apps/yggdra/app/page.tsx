'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { loadOshi } from '@/lib/storage';

export default function HomePage() {
  const [oshi, setOshi] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    setOshi(loadOshi());
    setIsReady(true);
  }, []);

  if (!isReady) {
    return (
      <main className="min-h-dvh bg-background flex items-center justify-center">
        <div className="text-muted-foreground text-sm">読み込み中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh bg-background flex flex-col items-center justify-center px-6 py-10">
      <div className="w-full max-w-sm flex flex-col items-center gap-8">
        {/* Logo / App Name */}
        <div className="flex flex-col items-center gap-3">
          <div className="flex items-center justify-center w-20 h-20 rounded-full bg-primary">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" className="text-primary-foreground">
              <path d="M20 4L24 14L34 14L26 21L29 32L20 25L11 32L14 21L6 14L16 14Z" fill="currentColor" />
            </svg>
          </div>
          <h1 className="font-display text-5xl font-bold text-foreground text-balance text-center">
            ゆぐどら!!
          </h1>
          <p className="text-base text-muted-foreground text-pretty text-center">
            {oshi ? 'おかえり！推しに会いに行こう' : 'あなたの推しアイドルを見つけよう'}
          </p>
        </div>

        <div className="relative w-full overflow-hidden rounded-[30px] border border-white/70 shadow-[0_24px_60px_rgba(232,93,117,0.16)]">
          <div className="relative aspect-[16/10]">
            <Image
              src="/images/ygd7-hero.jpg"
              alt="YGD7 hero"
              fill
              priority
              className="object-cover"
              sizes="(max-width: 640px) 100vw, 384px"
            />
            <div className="absolute inset-0 bg-[linear-gradient(180deg,_rgba(45,35,48,0.1)_0%,_rgba(45,35,48,0.48)_100%)]" />
            <div className="absolute inset-x-0 bottom-0 p-5 text-white">
              <p className="font-display text-[1.8rem] font-extrabold tracking-[0.08em]">
                YGD7!! YGGDRA
              </p>
              <p className="mt-1 text-sm text-white/88">
                bright pop idol matching experience
              </p>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="w-full flex flex-col gap-4">
          {oshi ? (
            <>
              <Link
                href="/oshi"
                className="flex items-center justify-center w-full py-4 rounded-full bg-primary text-primary-foreground font-bold text-lg transition-transform duration-200 active:scale-95"
              >
                推しに会いに行く
              </Link>
              <Link
                href="/tarot"
                className="flex items-center justify-center w-full py-3.5 rounded-full border-2 border-primary text-primary font-bold text-base transition-transform duration-200 active:scale-95"
              >
                占いのお部屋
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/diagnosis"
                className="flex items-center justify-center w-full py-4 rounded-full bg-primary text-primary-foreground font-bold text-lg transition-transform duration-200 active:scale-95"
              >
                カップル診断スタート
              </Link>
              <Link
                href="/tarot"
                className="flex items-center justify-center w-full py-3.5 rounded-full border-2 border-primary text-primary font-bold text-base transition-transform duration-200 active:scale-95"
              >
                占いのお部屋
              </Link>
            </>
          )}
        </div>

        {/* Decorative elements */}
        <div className="flex items-center gap-2 text-accent">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" />
          </svg>
          <svg width="10" height="10" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" />
          </svg>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" />
          </svg>
        </div>
      </div>
    </main>
  );
}
