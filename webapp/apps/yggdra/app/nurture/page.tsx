'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { Host } from '@yggdra/shared';
import { AvatarPlaceholder } from '@/components/avatar-placeholder';
import { characters } from '@/data/characters';
import { loadOshi } from '@/lib/storage';
import {
  ACTION_ICON,
  DEFAULT_NURTURE_STATE,
  getLevelProgress,
  getMoodLabel,
  ITEM_OPTIONS,
  type NurtureActionType,
  type NurtureChatMessage,
  type NurturePostResponse,
  type NurtureStats,
} from '@/lib/nurture';

const ITEM_ORDER = ['snack', 'present', 'training', 'champagne'] as const;

export default function NurturePage() {
  const router = useRouter();
  const chatViewportRef = useRef<HTMLDivElement>(null);
  const [character, setCharacter] = useState<Host | null>(null);
  const [state, setState] = useState<NurtureStats>(DEFAULT_NURTURE_STATE);
  const [messages, setMessages] = useState<NurtureChatMessage[]>([]);
  const [draft, setDraft] = useState('');
  const [pendingAction, setPendingAction] = useState<NurtureActionType | null>(null);
  const [pendingContent, setPendingContent] = useState('');
  const [isBooting, setIsBooting] = useState(true);
  const [error, setError] = useState('');
  const [levelUpModal, setLevelUpModal] = useState<{ level: number } | null>(null);

  useEffect(() => {
    const selectedId = loadOshi();

    if (!selectedId) {
      router.replace('/diagnosis');
      return;
    }

    const found = characters.find((entry) => entry.id === selectedId);
    if (!found) {
      router.replace('/diagnosis');
      return;
    }

    const selectedCharacter = found;

    setCharacter(selectedCharacter);

    const controller = new AbortController();

    async function bootstrap() {
      try {
        const response = await fetch(`/api/nurture?characterId=${selectedCharacter.id}`, {
          method: 'GET',
          signal: controller.signal,
          cache: 'no-store',
        });

        const data = (await response.json()) as {
          state?: NurtureStats;
          messages?: NurtureChatMessage[];
          error?: string;
        };

        if (!response.ok) {
          throw new Error(data.error ?? '育成データの取得に失敗しました');
        }

        if (data.state) {
          setState(data.state);
        }

        if (Array.isArray(data.messages)) {
          setMessages(data.messages);
        }
      } catch (fetchError) {
        if (controller.signal.aborted) {
          return;
        }

        setError(
          fetchError instanceof Error
            ? fetchError.message
            : '育成データの取得に失敗しました'
        );
      } finally {
        if (!controller.signal.aborted) {
          setIsBooting(false);
        }
      }
    }

    void bootstrap();

    return () => controller.abort();
  }, [router]);

  useEffect(() => {
    const node = chatViewportRef.current;
    if (!node) return;

    node.scrollTo({
      top: node.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, pendingAction]);

  if (!character || isBooting) {
    return (
      <main className="flex min-h-dvh items-center justify-center bg-background px-6">
        <div className="text-sm text-muted-foreground">育成ルームを準備中...</div>
      </main>
    );
  }

  const pendingUserMessage =
    pendingAction && pendingContent
      ? {
          id: 'pending-user',
          role: 'user' as const,
          actionType: pendingAction,
          content: pendingContent,
          createdAt: new Date().toISOString(),
        }
      : null;

  const renderedMessages = pendingUserMessage
    ? [...messages, pendingUserMessage]
    : messages;

  async function submitAction(actionType: NurtureActionType, content?: string) {
    if (!character || pendingAction) {
      return;
    }

    const resolvedContent =
      actionType === 'message'
        ? content?.trim() ?? ''
        : ITEM_OPTIONS[actionType].logLabel;

    if (actionType === 'message' && !resolvedContent) {
      return;
    }

    setError('');
    setPendingAction(actionType);
    setPendingContent(resolvedContent);

    try {
      const response = await fetch('/api/nurture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          characterId: character.id,
          actionType,
          message: actionType === 'message' ? resolvedContent : undefined,
          currentState: state,
          recentMessages: messages.slice(-5),
        }),
      });

      const data = (await response.json()) as NurturePostResponse & {
        error?: string;
      };

      if (!response.ok) {
        throw new Error(data.error ?? '育成アクションの送信に失敗しました');
      }

      setState(data.state);
      setMessages(data.messages);

      if (data.leveledUp) {
        setLevelUpModal({ level: data.state.level });
      }

      if (actionType === 'message') {
        setDraft('');
      }
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : '育成アクションの送信に失敗しました'
      );
    } finally {
      setPendingAction(null);
      setPendingContent('');
    }
  }

  return (
    <main className="min-h-dvh bg-[radial-gradient(circle_at_top,_rgba(232,93,117,0.14),_transparent_32%),linear-gradient(180deg,_#fff8f3_0%,_#faf7f5_45%,_#f9f2ff_100%)] px-4 py-6">
      <div className="mx-auto flex w-full max-w-md flex-col gap-4">
        <div className="flex items-center justify-between">
          <Link
            href="/oshi"
            className="flex items-center gap-1 text-sm text-muted-foreground"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 12L6 8L10 4" />
            </svg>
            推しページへ
          </Link>
          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
            育成ルーム
          </span>
        </div>

        <section className="rounded-[28px] border border-white/70 bg-card/90 p-5 shadow-[0_20px_60px_rgba(232,93,117,0.12)] backdrop-blur">
          <div className="flex items-center gap-4">
            <AvatarPlaceholder
              characterId={character.id}
              name={character.displayName}
              size="md"
            />
            <div className="min-w-0 flex-1">
              <h1 className="font-display text-2xl font-bold text-foreground">
                {character.displayName}
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                気分: {getMoodLabel(state.mood)}
              </p>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-4">
            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">育成度</span>
                <span className="font-semibold text-foreground">Lv. {state.level}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${getLevelProgress(state.level)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">親密度</span>
                <span className="font-semibold text-foreground">
                  {state.intimacy} / 100
                </span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-accent"
                  style={{ width: `${state.intimacy}%` }}
                />
              </div>
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">機嫌</span>
                <span className="font-semibold text-foreground">{state.mood} / 100</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-secondary"
                  style={{ width: `${state.mood}%` }}
                />
              </div>
            </div>
          </div>
        </section>

        <section className="overflow-hidden rounded-[28px] border border-white/70 bg-card/95 shadow-[0_20px_50px_rgba(196,181,253,0.16)]">
          <div
            ref={chatViewportRef}
            className="flex h-[46dvh] flex-col gap-3 overflow-y-auto px-4 py-5"
          >
            {renderedMessages.length === 0 && (
              <div className="rounded-2xl bg-muted px-4 py-3 text-sm text-muted-foreground">
                ここから育成スタート。アイテムを渡したり、やさしく話しかけてみて。
              </div>
            )}

            {renderedMessages.map((message) => {
              const isCharacter = message.role === 'character';

              return (
                <div
                  key={message.id}
                  className={`flex items-end gap-2 ${isCharacter ? 'justify-start' : 'justify-end'}`}
                >
                  {isCharacter && (
                    <AvatarPlaceholder
                      characterId={character.id}
                      name={character.displayName}
                      size="sm"
                      className="h-10 w-10 text-sm"
                    />
                  )}

                  <div
                    className={`max-w-[78%] rounded-[22px] px-4 py-3 text-sm leading-6 ${
                      isCharacter
                        ? 'rounded-bl-md bg-muted text-foreground'
                        : 'rounded-br-md bg-primary text-primary-foreground'
                    }`}
                  >
                    {!isCharacter && (
                      <div className="mb-1 text-xs font-semibold opacity-85">
                        {ACTION_ICON[message.actionType]} あなた
                      </div>
                    )}
                    {message.content}
                  </div>

                  {!isCharacter && (
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/25 text-lg">
                      {ACTION_ICON[message.actionType]}
                    </div>
                  )}
                </div>
              );
            })}

            {pendingAction && (
              <div className="flex items-end gap-2">
                <AvatarPlaceholder
                  characterId={character.id}
                  name={character.displayName}
                  size="sm"
                  className="h-10 w-10 text-sm"
                />
                <div className="rounded-[22px] rounded-bl-md bg-muted px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-secondary animate-pulse" />
                    <span className="h-2 w-2 rounded-full bg-secondary animate-pulse [animation-delay:120ms]" />
                    <span className="h-2 w-2 rounded-full bg-secondary animate-pulse [animation-delay:240ms]" />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-border/80 bg-background/70 px-4 py-4">
            <div className="grid grid-cols-4 gap-2">
              {ITEM_ORDER.map((itemKey) => (
                <button
                  key={itemKey}
                  type="button"
                  disabled={Boolean(pendingAction)}
                  onClick={() => void submitAction(itemKey)}
                  className="rounded-2xl bg-white px-2 py-3 text-center text-xs font-semibold text-foreground shadow-sm ring-1 ring-border transition-transform duration-200 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <div className="text-lg">{ITEM_OPTIONS[itemKey].icon}</div>
                  <div className="mt-1">{ITEM_OPTIONS[itemKey].label}</div>
                </button>
              ))}
            </div>

            <form
              className="mt-3 flex items-end gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                void submitAction('message', draft);
              }}
            >
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="やさしく話しかけてみる..."
                rows={2}
                disabled={Boolean(pendingAction)}
                className="min-h-20 flex-1 resize-none rounded-3xl border border-border bg-card px-4 py-3 text-sm text-foreground outline-none transition focus:border-primary"
              />
              <button
                type="submit"
                disabled={Boolean(pendingAction) || draft.trim().length === 0}
                className="rounded-full bg-primary px-5 py-3 font-bold text-primary-foreground transition-transform duration-200 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
              >
                送信
              </button>
            </form>

            {error && (
              <p className="mt-3 text-sm text-primary">{error}</p>
            )}
          </div>
        </section>
      </div>

      {levelUpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/45 px-6">
          <div className="w-full max-w-sm rounded-[32px] bg-card px-6 py-8 text-center shadow-[0_30px_80px_rgba(45,35,48,0.22)]">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-accent/20 text-3xl">
              ✨
            </div>
            <h2 className="mt-4 font-display text-2xl font-bold text-foreground">
              Level Up
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              親密度が100に到達。{character.displayName}との絆が深まって、
              Lv. {levelUpModal.level} になりました。
            </p>
            <button
              type="button"
              onClick={() => setLevelUpModal(null)}
              className="mt-6 rounded-full bg-primary px-6 py-3 font-bold text-primary-foreground"
            >
              続ける
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
