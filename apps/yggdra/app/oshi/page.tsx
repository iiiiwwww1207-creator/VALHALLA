'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import type { Host } from '@yggdra/shared';
import { characters } from '@/data/characters';
import { loadOshi } from '@/lib/storage';
import { AvatarPlaceholder } from '@/components/avatar-placeholder';
import {
  getLevelProgress,
  getMoodLabel,
  OSHI_FALLBACK_STATE,
  type NurtureStats,
} from '@/lib/nurture';

const personalityLabels: Record<string, string> = {
  tsundere: 'ツンデレ',
  oraora: 'オラオラ',
  healing: 'いやし',
  calm: '安心',
  flashy: 'ギラギラ',
  adhd: 'ADHD系',
};

const styleLabels: Record<string, string> = {
  calm: '癒やし',
  energetic: '盛り上げ',
  mature: '大人',
  passionate: '情熱',
  healing: 'ヒーリング',
  intellectual: '知的',
  sweet_talker: '甘い言葉',
  big_brother: 'お兄さん',
};

const faceLabels: Record<string, string> = {
  korean: '韓国系',
  johnny: 'ジャニーズ系',
  wild: 'ワイルド',
  dog: '犬系',
  cat: '猫系',
};

export default function OshiPage() {
  const router = useRouter();
  const [character, setCharacter] = useState<Host | null>(null);
  const [showComingSoon, setShowComingSoon] = useState(false);
  const [isReady, setIsReady] = useState(false);
  const [nurtureStats, setNurtureStats] = useState<NurtureStats>(OSHI_FALLBACK_STATE);

  useEffect(() => {
    const oshiId = loadOshi();
    if (!oshiId) {
      router.replace('/diagnosis');
      return;
    }
    const found = characters.find((c) => c.id === oshiId);
    if (!found) {
      router.replace('/diagnosis');
      return;
    }
    setCharacter(found);
    setIsReady(true);
  }, [router]);

  useEffect(() => {
    if (!character) return;

    const selectedCharacter = character;
    const controller = new AbortController();

    async function loadNurtureStats() {
      try {
        const response = await fetch(`/api/nurture?characterId=${selectedCharacter.id}`, {
          cache: 'no-store',
          signal: controller.signal,
        });

        if (!response.ok) {
          return;
        }

        const data = (await response.json()) as {
          state?: NurtureStats;
          databaseAvailable?: boolean;
        };

        if (data.databaseAvailable && data.state) {
          setNurtureStats(data.state);
        }
      } catch {
        // Keep the static preview when DB is not available.
      }
    }

    void loadNurtureStats();

    return () => controller.abort();
  }, [character]);

  if (!isReady || !character) {
    return (
      <main className="min-h-dvh bg-background flex items-center justify-center px-6">
        <div className="text-muted-foreground text-sm">読み込み中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh bg-background px-6 py-8 relative">
      <div className="w-full max-w-sm mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Link
            href="/"
            className="text-sm text-muted-foreground flex items-center gap-1"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 12L6 8L10 4" />
            </svg>
            トップ
          </Link>
          <span className="text-xs text-accent font-bold">MY 推し</span>
        </div>

        {/* Hero */}
        <div className="flex flex-col items-center gap-4 mb-8">
          <AvatarPlaceholder
            characterId={character.id}
            name={character.displayName}
            size="lg"
          />
          <div className="text-center">
            <h1 className="font-display text-3xl font-bold text-foreground text-balance">
              {character.displayName}
            </h1>
            <p className="text-sm text-muted-foreground mt-2 text-pretty">
              {character.catchCopy}
            </p>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {character.personalityTags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-xs font-medium"
            >
              {personalityLabels[tag] ?? tag}
            </span>
          ))}
          <span className="px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
            {styleLabels[character.primaryStyleTag] ?? character.primaryStyleTag}
          </span>
          <span className="px-3 py-1.5 rounded-full bg-muted text-muted-foreground text-xs font-medium">
            {faceLabels[character.faceType] ?? character.faceType}
          </span>
        </div>

        {/* Status preview */}
        <div className="bg-card rounded-3xl border border-border p-5 mb-6">
          <h2 className="font-display text-lg font-bold text-foreground mb-4">
            ステータス
          </h2>
          <div className="flex flex-col gap-4">
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-muted-foreground">育成度</span>
                <span className="text-foreground font-medium">Lv. {nurtureStats.level}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${getLevelProgress(nurtureStats.level)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-muted-foreground">親密度</span>
                <span className="text-foreground font-medium">
                  {nurtureStats.intimacy} / 100
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-accent"
                  style={{ width: `${nurtureStats.intimacy}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-muted-foreground">機嫌</span>
                <span className="text-foreground font-medium">
                  {getMoodLabel(nurtureStats.mood)}
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-secondary"
                  style={{ width: `${nurtureStats.mood}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Profile details */}
        <div className="bg-card rounded-3xl border border-border p-5 mb-6">
          <h2 className="font-display text-lg font-bold text-foreground mb-4">
            プロフィール
          </h2>
          <div className="flex flex-col gap-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">趣味</span>
              <span className="text-foreground text-right">{character.hobbies.join('、')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">好きな音楽</span>
              <span className="text-foreground text-right">{character.musicGenres.join('、')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">大切にしていること</span>
            </div>
            <p className="text-foreground text-pretty">{character.coreValue}</p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col gap-3 mb-8">
          <Link
            href="/nurture"
            className="w-full py-3.5 rounded-full bg-primary text-primary-foreground font-bold text-base text-center transition-transform duration-200 active:scale-95"
          >
            育成する
          </Link>
          <button
            type="button"
            onClick={() => setShowComingSoon(true)}
            className="w-full py-3.5 rounded-full border-2 border-primary text-primary font-bold text-base transition-transform duration-200 active:scale-95"
          >
            もっと見たい！
          </button>
          <button
            type="button"
            onClick={() => setShowComingSoon(true)}
            className="w-full py-3.5 rounded-full border-2 border-accent text-foreground font-bold text-base transition-transform duration-200 active:scale-95"
          >
            店舗予約
          </button>
        </div>

        {/* Bottom links */}
        <div className="flex justify-center gap-6 text-sm">
          <Link href="/tarot" className="text-primary font-medium">
            タロット占い
          </Link>
          <Link href="/diagnosis" className="text-muted-foreground">
            再診断
          </Link>
        </div>
      </div>

      {/* Coming Soon Overlay */}
      {showComingSoon && (
        <div
          className="fixed inset-0 bg-foreground/50 flex items-center justify-center z-50 px-6"
          onClick={() => setShowComingSoon(false)}
        >
          <div
            className="bg-card rounded-3xl p-8 max-w-sm w-full text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-center mb-4">
              <svg width="48" height="48" viewBox="0 0 16 16" fill="none" className="text-accent">
                <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" fill="currentColor" />
              </svg>
            </div>
            <h3 className="font-display text-xl font-bold text-foreground mb-2">
              Coming Soon
            </h3>
            <p className="text-sm text-muted-foreground text-pretty mb-6">
              この機能は現在準備中です。お楽しみに！
            </p>
            <button
              type="button"
              onClick={() => setShowComingSoon(false)}
              className="px-8 py-3 rounded-full bg-primary text-primary-foreground font-bold text-sm transition-transform duration-200 active:scale-95"
            >
              閉じる
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
