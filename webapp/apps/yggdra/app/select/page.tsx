'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { getTopMatches } from '@yggdra/shared';
import type { DiagnosisResult } from '@yggdra/shared';
import { characters } from '@/data/characters';
import { loadDiagnosisState, saveOshi } from '@/lib/storage';
import { AvatarPlaceholder } from '@/components/avatar-placeholder';

// Label maps for display
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

export default function SelectPage() {
  const router = useRouter();
  const [results, setResults] = useState<DiagnosisResult[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const state = loadDiagnosisState();
    if (!state?.completedAt || !state.answers.length) {
      router.replace('/diagnosis');
      return;
    }
    const top = getTopMatches(state.answers, characters, 3);
    setResults(top);
    setIsReady(true);
  }, [router]);

  const handleSelect = (hostId: string) => {
    saveOshi(hostId);
    router.push('/oshi');
  };

  if (!isReady) {
    return (
      <main className="min-h-dvh bg-background flex items-center justify-center px-6">
        <div className="text-muted-foreground text-sm">結果を計算中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh bg-background px-6 py-8">
      <div className="w-full max-w-sm mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-bold text-foreground text-balance mb-3">
            あなたにぴったりのアイドル
          </h1>
          <p className="text-base text-muted-foreground text-pretty">
            この子たちが、あなたを待っています
          </p>
        </div>

        <div className="relative mb-8 overflow-hidden rounded-[28px] border border-white/70 shadow-[0_24px_60px_rgba(196,181,253,0.18)]">
          <div className="relative aspect-[16/9]">
            <Image
              src="/images/ygd7-hero.jpg"
              alt="YGD7 group hero"
              fill
              className="object-cover"
              sizes="(max-width: 640px) 100vw, 384px"
            />
            <div className="absolute inset-0 bg-[linear-gradient(135deg,_rgba(45,35,48,0.42)_0%,_rgba(45,35,48,0.08)_55%,_rgba(232,93,117,0.18)_100%)]" />
            <div className="absolute inset-x-0 bottom-0 p-5 text-white">
              <p className="font-display text-[1.65rem] font-extrabold tracking-[0.08em]">
                YGD7!! YGGDRA
              </p>
              <p className="mt-1 text-sm text-white/88">
                あなたの推し候補たちをチェック
              </p>
            </div>
          </div>
        </div>

        {/* Result cards */}
        <div className="flex flex-col gap-5">
          {results.map((result, index) => {
            const character = characters.find((c) => c.id === result.hostId);
            if (!character) return null;

            return (
              <div
                key={character.id}
                className="bg-card rounded-3xl border border-border p-5 flex flex-col items-center gap-4"
              >
                {/* Rank badge */}
                <div className="flex items-center gap-2">
                  <span className="text-accent text-sm font-bold">
                    {index === 0 ? '1st' : index === 1 ? '2nd' : '3rd'}
                  </span>
                  <span className="text-sm text-muted-foreground">Match</span>
                </div>

                {/* Avatar */}
                <AvatarPlaceholder
                  characterId={character.id}
                  name={character.displayName}
                  size="lg"
                />

                {/* Name + match % */}
                <div className="text-center">
                  <h2 className="font-display text-xl font-bold text-foreground">
                    {character.displayName}
                  </h2>
                  <p className="text-primary font-bold text-lg mt-1">
                    {result.score}% マッチ
                  </p>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap justify-center gap-2">
                  {character.personalityTags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-medium"
                    >
                      {personalityLabels[tag] ?? tag}
                    </span>
                  ))}
                  <span className="px-3 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium">
                    {styleLabels[character.primaryStyleTag] ?? character.primaryStyleTag}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-muted text-muted-foreground text-xs font-medium">
                    {faceLabels[character.faceType] ?? character.faceType}
                  </span>
                </div>

                {/* Match reasons */}
                <div className="flex flex-col gap-1 w-full">
                  {result.matchReasons.map((reason, i) => (
                    <p key={i} className="text-xs text-muted-foreground text-center">
                      {reason}
                    </p>
                  ))}
                </div>

                {/* Select button */}
                <button
                  type="button"
                  onClick={() => handleSelect(character.id)}
                  className="w-full py-3.5 rounded-full bg-primary text-primary-foreground font-bold text-base transition-transform duration-200 active:scale-95"
                >
                  この子を推す！
                </button>
              </div>
            );
          })}
        </div>

        {/* Back link */}
        <div className="mt-8 text-center">
          <button
            type="button"
            onClick={() => router.push('/diagnosis')}
            className="text-sm text-muted-foreground underline"
          >
            もう一度診断する
          </button>
        </div>
      </div>
    </main>
  );
}
