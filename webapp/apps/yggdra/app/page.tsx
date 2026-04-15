'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { loadOshi } from '@/lib/storage';

function Sparkle({ className, delay }: { className?: string; delay?: string }) {
  return (
    <svg
      width="16" height="16" viewBox="0 0 16 16" fill="currentColor"
      className={className}
      style={{ animationDelay: delay }}
    >
      <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" />
    </svg>
  );
}

export default function HomePage() {
  const [oshi, setOshi] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setOshi(loadOshi());
    setIsReady(true);
    const t = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  if (!isReady) {
    return (
      <main className="min-h-dvh bg-black flex items-center justify-center">
        <div className="text-white/40 text-sm">...</div>
      </main>
    );
  }

  return (
    <main className="relative min-h-dvh flex flex-col overflow-hidden bg-black">
      {/* Full-screen hero image */}
      <div className="absolute inset-0">
        <Image
          src="/images/ygd7-hero-2x.jpg"
          alt="YGD7 YGGDRA"
          fill
          priority
          className="object-cover object-top scale-105"
          sizes="100vw"
        />
        {/* Dreamy pink-purple overlay */}
        <div className="absolute inset-0 bg-[rgba(180,100,200,0.12)]" />
        {/* Bottom fade for text readability */}
        <div className="absolute inset-0 bg-[linear-gradient(0deg,rgba(10,0,15,0.92)_0%,rgba(10,0,15,0.6)_35%,rgba(10,0,15,0.05)_60%,transparent_100%)]" />
      </div>

      {/* Floating sparkles */}
      <div className="absolute inset-0 z-10 pointer-events-none">
        <Sparkle
          className="absolute top-[12%] left-[8%] text-pink-300/50 w-3 h-3 animate-[float_4s_ease-in-out_infinite]"
          delay="0s"
        />
        <Sparkle
          className="absolute top-[18%] right-[12%] text-white/40 w-2 h-2 animate-[float_3.5s_ease-in-out_infinite]"
          delay="0.8s"
        />
        <Sparkle
          className="absolute top-[45%] left-[15%] text-purple-300/40 w-2.5 h-2.5 animate-[float_5s_ease-in-out_infinite]"
          delay="1.5s"
        />
        <Sparkle
          className="absolute top-[35%] right-[20%] text-pink-200/30 w-2 h-2 animate-[float_4.5s_ease-in-out_infinite]"
          delay="2s"
        />
        <Sparkle
          className="absolute bottom-[30%] left-[25%] text-white/25 w-1.5 h-1.5 animate-[float_3s_ease-in-out_infinite]"
          delay="0.5s"
        />
      </div>

      {/* Content — pinned to bottom */}
      <div className="relative z-20 flex flex-col flex-1 justify-end">
        <div className="px-7 pb-10 pt-24">
          <div className="w-full max-w-sm mx-auto flex flex-col gap-7">
            {/* Logo / Title group */}
            <div
              className={`flex flex-col gap-2 transition-all duration-700 ease-out ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
              }`}
            >
              <p className="text-sm font-bold text-pink-300/90 uppercase">
                Welcome Style
              </p>
              <h1 className="font-display text-[3.2rem] leading-[0.95] font-extrabold text-white drop-shadow-[0_4px_24px_rgba(236,72,153,0.3)]">
                <span className="text-balance">ゆぐどら!!</span>
              </h1>
              <p className="text-base text-white/75 text-pretty mt-1">
                {oshi ? 'おかえり！推しに会いに行こう' : 'あなたの推しアイドルを見つけよう'}
              </p>
            </div>

            {/* CTA Buttons */}
            <div
              className={`flex flex-col gap-3 transition-all duration-700 ease-out delay-200 ${
                isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
              }`}
              style={{ transitionDelay: '200ms' }}
            >
              {oshi ? (
                <>
                  <Link
                    href="/oshi"
                    className="flex items-center justify-center w-full py-4 rounded-full bg-white/95 backdrop-blur text-foreground font-bold text-lg transition-transform duration-200 active:scale-95 shadow-[0_8px_32px_rgba(236,72,153,0.25)]"
                  >
                    推しに会いに行く
                  </Link>
                  <Link
                    href="/tarot"
                    className="flex items-center justify-center w-full py-3.5 rounded-full border border-white/30 bg-white/10 backdrop-blur text-white font-bold text-base transition-transform duration-200 active:scale-95"
                  >
                    占いのお部屋
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/diagnosis"
                    className="flex items-center justify-center w-full py-4 rounded-full bg-white/95 backdrop-blur text-foreground font-bold text-lg transition-transform duration-200 active:scale-95 shadow-[0_8px_32px_rgba(236,72,153,0.25)]"
                  >
                    カップル診断スタート
                  </Link>
                  <Link
                    href="/tarot"
                    className="flex items-center justify-center w-full py-3.5 rounded-full border border-white/30 bg-white/10 backdrop-blur text-white font-bold text-base transition-transform duration-200 active:scale-95"
                  >
                    占いのお部屋
                  </Link>
                </>
              )}
            </div>

            {/* Bottom accent */}
            <div
              className={`flex items-center justify-center gap-3 transition-all duration-700 ease-out ${
                isVisible ? 'opacity-100' : 'opacity-0'
              }`}
              style={{ transitionDelay: '500ms' }}
            >
              <div className="h-px flex-1 bg-white/15" />
              <div className="flex items-center gap-1.5 text-pink-300/60">
                <Sparkle className="w-2.5 h-2.5" />
                <span className="text-[10px] font-bold text-white/30 uppercase">
                  YGD7
                </span>
                <Sparkle className="w-2.5 h-2.5" />
              </div>
              <div className="h-px flex-1 bg-white/15" />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
