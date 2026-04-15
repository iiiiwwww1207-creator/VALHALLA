'use client';

import type { CSSProperties } from 'react';
import { CHARACTER_COLORS } from '@/data/characters';

interface IdolCardAvatarProps {
  characterId: string;
  name: string;
  catchCopy: string;
  isSpeaking?: boolean;
  className?: string;
}

function normalizeHex(hex: string) {
  const value = hex.replace('#', '').trim();

  if (value.length === 3) {
    return value
      .split('')
      .map((char) => char + char)
      .join('');
  }

  return value.padEnd(6, '0').slice(0, 6);
}

function hexToRgb(hex: string) {
  const value = normalizeHex(hex);
  const parsed = Number.parseInt(value, 16);

  return {
    r: (parsed >> 16) & 255,
    g: (parsed >> 8) & 255,
    b: parsed & 255,
  };
}

function mixHex(base: string, mixin: string, amount: number) {
  const start = hexToRgb(base);
  const end = hexToRgb(mixin);
  const clampedAmount = Math.max(0, Math.min(1, amount));

  const channel = (from: number, to: number) =>
    Math.round(from + (to - from) * clampedAmount)
      .toString(16)
      .padStart(2, '0');

  return `#${channel(start.r, end.r)}${channel(start.g, end.g)}${channel(start.b, end.b)}`;
}

function hexToRgba(hex: string, alpha: number) {
  const { r, g, b } = hexToRgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function IdolCardAvatar({
  characterId,
  name,
  catchCopy,
  isSpeaking = false,
  className = '',
}: IdolCardAvatarProps) {
  const palette = CHARACTER_COLORS[characterId] ?? { bg: '#e0e0e0', text: '#333333' };
  const initial = name.charAt(0);
  const accent = mixHex(palette.bg, palette.text, 0.34);
  const highlight = mixHex(palette.bg, '#ffffff', 0.5);
  const deepTone = mixHex(palette.text, '#0f172a', 0.28);
  const cardStyle = {
    '--idol-border': hexToRgba(highlight, 0.92),
    '--idol-shadow': hexToRgba(deepTone, 0.22),
  } as CSSProperties;

  return (
    <div className={`idol-card-shell mx-auto w-full max-w-[290px] ${className}`}>
      <div
        className={`idol-card-frame relative aspect-[4/5] overflow-hidden rounded-[34px] ${isSpeaking ? 'is-speaking' : ''}`}
        style={cardStyle}
      >
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(145deg, ${deepTone} 0%, ${accent} 26%, ${palette.bg} 58%, ${highlight} 100%)`,
          }}
        />
        <div
          className="absolute inset-0 opacity-28 mix-blend-screen"
          style={{
            backgroundImage: 'url(/images/ygd7-hero.jpg)',
            backgroundPosition: 'center top',
            backgroundRepeat: 'no-repeat',
            backgroundSize: 'cover',
          }}
        />
        <div
          className="absolute inset-0"
          style={{
            background: `radial-gradient(circle at 16% 16%, ${hexToRgba('#ffffff', 0.72)} 0%, transparent 30%), radial-gradient(circle at 85% 18%, ${hexToRgba(palette.bg, 0.36)} 0%, transparent 24%), linear-gradient(180deg, ${hexToRgba('#ffffff', 0.12)} 0%, ${hexToRgba(deepTone, 0.26)} 100%)`,
          }}
        />

        <div className="absolute inset-x-4 top-4 z-10 flex items-start justify-between gap-3">
          <div className="rounded-full border border-white/35 bg-white/18 px-3 py-1 text-[10px] font-bold tracking-[0.28em] text-white/90 backdrop-blur-sm">
            IDOL CARD
          </div>
          <div
            className={`rounded-full px-3 py-1 text-[10px] font-bold tracking-[0.2em] backdrop-blur-sm ${
              isSpeaking
                ? 'bg-white/85 text-primary'
                : 'border border-white/28 bg-white/16 text-white/80'
            }`}
          >
            {isSpeaking ? 'LIVE' : 'AURA'}
          </div>
        </div>

        <div className="absolute -left-3 bottom-24 z-10 select-none text-[7.5rem] font-black italic leading-none tracking-[-0.1em] text-white/78 drop-shadow-[0_10px_20px_rgba(45,35,48,0.22)]">
          {initial}
        </div>

        <div className="absolute bottom-0 left-0 right-0 z-10 p-4">
          <div className="rounded-[28px] border border-white/40 bg-white/16 p-4 text-white backdrop-blur-md">
            <div className="text-[10px] font-semibold tracking-[0.28em] text-white/72">
              NURTURE SESSION
            </div>
            <h2 className="mt-2 font-display text-[1.85rem] font-black leading-tight drop-shadow-[0_4px_12px_rgba(45,35,48,0.18)]">
              {name}
            </h2>
            <p className="mt-2 text-sm leading-6 text-white/88">{catchCopy}</p>
          </div>
        </div>

        <div className="absolute right-4 top-[4.5rem] h-16 w-16 rounded-full border border-white/30 bg-white/12 blur-[1px]" />
        <div className="absolute right-8 top-24 h-6 w-6 rounded-full bg-white/35" />
      </div>
    </div>
  );
}
