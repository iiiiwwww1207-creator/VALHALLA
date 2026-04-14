'use client';

import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-dvh bg-background flex flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm flex flex-col items-center gap-10">
        {/* Logo / App Name */}
        <div className="flex flex-col items-center gap-3">
          <div className="flex items-center justify-center w-20 h-20 rounded-full bg-primary">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" className="text-primary-foreground">
              <path d="M20 4L24 14L34 14L26 21L29 32L20 25L11 32L14 21L6 14L16 14Z" fill="currentColor" />
            </svg>
          </div>
          <h1 className="font-display text-5xl font-bold text-foreground text-balance text-center">
            ユグドラ
          </h1>
          <p className="text-base text-muted-foreground text-pretty text-center">
            あなたの推しアイドルを見つけよう
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="w-full flex flex-col gap-4">
          <Link
            href="/diagnosis"
            className="flex items-center justify-center w-full py-4 rounded-full bg-primary text-primary-foreground font-bold text-lg transition-transform duration-200 active:scale-95"
          >
            診断スタート
          </Link>

          <Link
            href="/tarot"
            className="flex items-center justify-center w-full py-3.5 rounded-full border-2 border-primary text-primary font-bold text-base transition-transform duration-200 active:scale-95"
          >
            毎日のタロット占い
          </Link>
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
