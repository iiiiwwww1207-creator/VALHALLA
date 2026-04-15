'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { TAROT_CARDS, drawDailyTarot } from '@yggdra/shared';
import { characters } from '@/data/characters';
import { AvatarPlaceholder } from '@/components/avatar-placeholder';
import { loadOshi, hasDoneTarotToday, saveTarotResult, loadTarotResult } from '@/lib/storage';

const HEALING_MESSAGES = [
  '僕がいるよ、今日も一緒にいるからね。',
  '大丈夫、きみならきっとうまくいくよ。',
  'どんな日も、きみは輝いてるよ。',
  'そばにいるから、安心してね。',
  '今日のきみも、とっても素敵だよ。',
];

function getHealingMessage(cardIndex: number): string {
  return HEALING_MESSAGES[cardIndex % HEALING_MESSAGES.length];
}

function getTodayString(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

export default function TarotPage() {
  const [selectedCard, setSelectedCard] = useState<number | null>(null);
  const [isReversed, setIsReversed] = useState(false);
  const [alreadyDone, setAlreadyDone] = useState(false);
  const [flippedCard, setFlippedCard] = useState<number | null>(null);
  const [oshiId, setOshiId] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  const today = getTodayString();

  useEffect(() => {
    const oshi = loadOshi();
    setOshiId(oshi);

    const existing = loadTarotResult(today);
    if (existing) {
      setSelectedCard(existing.cardIndex);
      setIsReversed(existing.isReversed);
      setFlippedCard(existing.cardIndex);
      setAlreadyDone(true);
    }
    setIsReady(true);
  }, [today]);

  const handleCardClick = (cardIndex: number) => {
    if (alreadyDone || selectedCard !== null) return;

    // Use deterministic draw based on a userId (or random for anonymous)
    const userId = oshiId ?? 'anonymous';
    const result = drawDailyTarot(userId, today);

    setSelectedCard(result.cardIndex);
    setIsReversed(result.isReversed);
    saveTarotResult(today, result.cardIndex, result.isReversed);
    setAlreadyDone(true);

    // Trigger flip animation
    setTimeout(() => {
      setFlippedCard(result.cardIndex);
    }, 100);
  };

  const oshiCharacter = characters.find((c) => c.id === oshiId) ?? characters[0];
  const drawnCard = selectedCard !== null ? TAROT_CARDS[selectedCard] : null;

  if (!isReady) {
    return (
      <main className="min-h-dvh bg-background flex items-center justify-center px-6">
        <div className="text-muted-foreground text-sm">読み込み中...</div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh bg-background px-6 py-8">
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
        </div>

        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-bold text-foreground text-balance mb-2">
            今日のタロット占い
          </h1>
          <p className="text-sm text-muted-foreground text-pretty">
            カードを1枚選んでタップしてね
          </p>
        </div>

        {/* Result display (after draw) */}
        {drawnCard && flippedCard !== null && (
          <div className="bg-card rounded-3xl border border-border p-6 mb-8 flex flex-col items-center gap-4">
            {/* Card name */}
            <div className="text-center">
              <div className="text-xs text-accent font-bold mb-1">
                {isReversed ? '逆位置' : '正位置'}
              </div>
              <h2 className="font-display text-2xl font-bold text-foreground">
                {drawnCard.name}
              </h2>
            </div>

            {/* Meaning */}
            <p className="text-sm text-foreground text-center text-pretty">
              {isReversed ? drawnCard.reversedMeaning : drawnCard.meaning}
            </p>

            {/* Oshi message */}
            <div className="w-full bg-muted rounded-2xl p-4 flex items-start gap-3">
              <AvatarPlaceholder
                characterId={oshiCharacter.id}
                name={oshiCharacter.displayName}
                size="sm"
              />
              <div className="flex-1">
                <p className="text-xs font-bold text-foreground mb-1">
                  {oshiCharacter.displayName}
                </p>
                <p className="text-sm text-muted-foreground text-pretty">
                  {getHealingMessage(selectedCard ?? 0)}
                </p>
              </div>
            </div>

            <p className="text-xs text-accent font-medium">
              今日はもう引いたよ
            </p>
          </div>
        )}

        {/* Card grid */}
        <div className="grid grid-cols-4 gap-2.5">
          {TAROT_CARDS.map((card, index) => {
            const isDrawn = flippedCard === index;
            const isDisabled = alreadyDone && !isDrawn;

            return (
              <button
                key={card.index}
                type="button"
                onClick={() => handleCardClick(index)}
                disabled={isDisabled || selectedCard !== null}
                className={`perspective-1000 aspect-[2/3] ${isDisabled ? 'opacity-40' : ''}`}
              >
                <div
                  className={`relative w-full h-full preserve-3d transition-transform duration-200 ${
                    isDrawn ? 'rotate-y-180' : ''
                  }`}
                >
                  {/* Card back */}
                  <div className="absolute inset-0 backface-hidden rounded-xl bg-primary flex items-center justify-center border-2 border-primary">
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="white" opacity={0.7}>
                      <path d="M8 0L9.5 6.5L16 8L9.5 9.5L8 16L6.5 9.5L0 8L6.5 6.5Z" />
                    </svg>
                  </div>

                  {/* Card front */}
                  <div className="absolute inset-0 backface-hidden rotate-y-180 rounded-xl bg-card border-2 border-accent flex flex-col items-center justify-center p-1">
                    <span className="text-accent text-xs font-bold">{card.index}</span>
                    <span className="text-foreground text-[10px] font-medium text-center leading-tight mt-0.5">
                      {card.name}
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Bottom nav */}
        <div className="mt-8 text-center">
          {oshiId ? (
            <Link href="/oshi" className="text-sm text-primary font-medium">
              推しのページへ
            </Link>
          ) : (
            <Link href="/diagnosis" className="text-sm text-primary font-medium">
              まずは診断してみよう
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}
