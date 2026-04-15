import 'server-only';

import { and, desc, eq } from 'drizzle-orm';
import type { Host } from '@yggdra/shared';
import { db, isDatabaseAvailable } from '@/db';
import { chatHistory, nurtureState } from '@/db/schema';
import { characters } from '@/data/characters';
import {
  clampStat,
  DEFAULT_NURTURE_STATE,
  getItemPromptLabel,
  ITEM_OPTIONS,
  type NurtureActionType,
  type NurtureChatMessage,
  type NurtureGetResponse,
  type NurturePostResponse,
  type NurtureStats,
} from '@/lib/nurture';

const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';

const PERSONA_STYLE_LABELS: Record<string, string> = {
  calm: '落ち着き',
  energetic: '元気',
  mature: '大人っぽさ',
  passionate: '情熱',
  healing: '癒やし',
  intellectual: '知的',
  sweet_talker: '甘い言葉',
  big_brother: '頼れるお兄さん',
};

const PERSONALITY_LABELS: Record<string, string> = {
  tsundere: 'ツンデレ',
  oraora: 'オラオラ',
  healing: '癒やし系',
  calm: '安心感',
  flashy: '華やか',
  adhd: '自由奔放',
};

const ITEM_RANGES = {
  snack: { intimacy: [3, 5], mood: [1, 3] },
  present: { intimacy: [2, 4], mood: [5, 8] },
  training: { intimacy: [1, 2], mood: [-2, 2] },
  champagne: { intimacy: [8, 12], mood: [5, 10] },
  message: { intimacy: [1, 4], mood: [0, 3] },
} as const;

export async function getNurtureSnapshot(
  userId: string,
  characterId: string
): Promise<NurtureGetResponse> {
  if (!isKnownCharacter(characterId)) {
    throw new Error('Unknown character');
  }

  if (!db || !isDatabaseAvailable()) {
    return {
      state: DEFAULT_NURTURE_STATE,
      messages: [],
      databaseAvailable: false,
    };
  }

  const state = await getOrCreateState(userId, characterId);
  const messages = await getRecentMessages(userId, characterId, 20);

  return {
    state,
    messages,
    databaseAvailable: true,
  };
}

export async function applyNurtureAction(input: {
  userId: string;
  characterId: string;
  actionType: NurtureActionType;
  message?: string;
  fallbackState?: NurtureStats;
  fallbackMessages?: NurtureChatMessage[];
}): Promise<NurturePostResponse> {
  const character = getCharacter(input.characterId);

  if (!character) {
    throw new Error('Unknown character');
  }

  const baseState =
    db && isDatabaseAvailable()
      ? await getOrCreateState(input.userId, input.characterId)
      : normalizeFallbackState(input.fallbackState ?? DEFAULT_NURTURE_STATE);

  const contextMessages =
    db && isDatabaseAvailable()
      ? await getRecentMessages(input.userId, input.characterId, 5)
      : (input.fallbackMessages ?? []).slice(-5);

  const userContent =
    input.actionType === 'message'
      ? input.message!.trim()
      : ITEM_OPTIONS[input.actionType].logLabel;

  const userMessage: NurtureChatMessage = {
    id: crypto.randomUUID(),
    role: 'user',
    actionType: input.actionType,
    content: userContent,
    createdAt: new Date().toISOString(),
  };

  const llmResult = await generateCharacterReaction({
    character,
    actionType: input.actionType,
    userContent,
    state: baseState,
    contextMessages,
  });

  const nextState = calculateNextState(baseState, llmResult.stats);

  const characterMessage: NurtureChatMessage = {
    id: crypto.randomUUID(),
    role: 'character',
    actionType: 'reply',
    content: llmResult.reply,
    createdAt: new Date().toISOString(),
  };

  if (db && isDatabaseAvailable()) {
    await db.insert(chatHistory).values([
      {
        id: userMessage.id,
        userId: input.userId,
        characterId: input.characterId,
        role: userMessage.role,
        actionType: userMessage.actionType,
        content: userMessage.content,
        createdAt: new Date(userMessage.createdAt),
      },
      {
        id: characterMessage.id,
        userId: input.userId,
        characterId: input.characterId,
        role: characterMessage.role,
        actionType: characterMessage.actionType,
        content: characterMessage.content,
        metadata: llmResult.stats,
        createdAt: new Date(characterMessage.createdAt),
      },
    ]);

    await db
      .update(nurtureState)
      .set({
        level: nextState.state.level,
        intimacy: nextState.state.intimacy,
        mood: nextState.state.mood,
        updatedAt: new Date(),
      })
      .where(
        and(
          eq(nurtureState.userId, input.userId),
          eq(nurtureState.characterId, input.characterId)
        )
      );

    return {
      state: nextState.state,
      messages: await getRecentMessages(input.userId, input.characterId, 20),
      appliedStats: llmResult.stats,
      leveledUp: nextState.leveledUp,
      databaseAvailable: true,
    };
  }

  return {
    state: nextState.state,
    messages: [...(input.fallbackMessages ?? []), userMessage, characterMessage].slice(-20),
    appliedStats: llmResult.stats,
    leveledUp: nextState.leveledUp,
    databaseAvailable: false,
  };
}

function getCharacter(characterId: string) {
  return characters.find((character) => character.id === characterId) ?? null;
}

function isKnownCharacter(characterId: string) {
  return characters.some((character) => character.id === characterId);
}

async function getOrCreateState(userId: string, characterId: string) {
  if (!db) {
    return DEFAULT_NURTURE_STATE;
  }

  const existing = await db.query.nurtureState.findFirst({
    where: and(
      eq(nurtureState.userId, userId),
      eq(nurtureState.characterId, characterId)
    ),
  });

  if (existing) {
    return {
      level: existing.level,
      intimacy: existing.intimacy,
      mood: existing.mood,
    };
  }

  await db.insert(nurtureState).values({
    userId,
    characterId,
    level: DEFAULT_NURTURE_STATE.level,
    intimacy: DEFAULT_NURTURE_STATE.intimacy,
    mood: DEFAULT_NURTURE_STATE.mood,
    updatedAt: new Date(),
  });

  return DEFAULT_NURTURE_STATE;
}

async function getRecentMessages(
  userId: string,
  characterId: string,
  limit: number
) {
  if (!db) {
    return [];
  }

  const rows = await db
    .select()
    .from(chatHistory)
    .where(
      and(eq(chatHistory.userId, userId), eq(chatHistory.characterId, characterId))
    )
    .orderBy(desc(chatHistory.createdAt), desc(chatHistory.id))
    .limit(limit);

  return rows
    .reverse()
    .map((row) => ({
      id: row.id,
      role: row.role as NurtureChatMessage['role'],
      actionType: row.actionType as NurtureChatMessage['actionType'],
      content: row.content,
      createdAt: row.createdAt.toISOString(),
    }));
}

async function generateCharacterReaction(input: {
  character: Host;
  actionType: NurtureActionType;
  userContent: string;
  state: NurtureStats;
  contextMessages: NurtureChatMessage[];
}) {
  const stats = ITEM_RANGES[input.actionType];
  const fallback = createFallbackReaction(input.character, input.actionType, input.userContent);
  const apiKey = process.env.OPENROUTER_API_KEY;

  if (!apiKey) {
    return {
      reply: fallback.reply,
      stats: fallback.stats,
    };
  }

  const systemPrompt = [
    `あなたはアイドルキャラクター「${input.character.displayName}」です。`,
    `キャッチコピー: ${input.character.catchCopy}`,
    `趣味: ${input.character.hobbies.join('、')}`,
    `好きな音楽: ${input.character.musicGenres.join('、')}`,
    `大切にしていること: ${input.character.coreValue}`,
    `接客スタイル: ${input.character.stylesTags.map((tag) => PERSONA_STYLE_LABELS[tag] ?? tag).join('、')}`,
    `性格: ${input.character.personalityTags.map((tag) => PERSONALITY_LABELS[tag] ?? tag).join('、')}`,
    '返答は必ず日本語で、癒やし系の優しいトーンにしてください。',
    'ユーザーへの返答本文は2〜3文だけにしてください。',
    '本文の後ろに [STATS]{"intimacy":整数,"mood":整数}[/STATS] を必ず1回だけ追加してください。',
    `今回の actionType は ${input.actionType} です。intimacy は ${stats.intimacy[0]}〜${stats.intimacy[1]} の範囲、mood は ${stats.mood[0]}〜${stats.mood[1]} の範囲の整数にしてください。`,
    '本文中で数値や STATS の存在を説明しないでください。',
  ].join('\n');

  const contextBlock =
    input.contextMessages.length === 0
      ? '直近の会話履歴はまだありません。'
      : input.contextMessages
          .map((message) => {
            const speaker = message.role === 'character' ? input.character.displayName : 'ユーザー';
            return `${speaker}: ${message.content}`;
          })
          .join('\n');

  const userPrompt = [
    `現在の状態: level=${input.state.level}, intimacy=${input.state.intimacy}, mood=${input.state.mood}`,
    `ユーザーの今回の行動: ${getItemPromptLabel(input.actionType, input.userContent)}`,
    '直近5件の会話:',
    contextBlock,
  ].join('\n');

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10_000);

    try {
      const response = await fetch(OPENROUTER_URL, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://yggdra.app',
          'X-Title': 'Yggdra Nurture',
        },
        body: JSON.stringify({
          model: 'openrouter/auto',
          temperature: 1,
          max_tokens: 220,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt },
          ],
        }),
        cache: 'no-store',
        signal: controller.signal,
      });

      if (!response.ok) {
        return {
          reply: fallback.reply,
          stats: fallback.stats,
        };
      }

      const data = (await response.json()) as {
        choices?: Array<{
          message?: {
            content?: string;
          };
        }>;
      };

      const rawContent = data.choices?.[0]?.message?.content?.trim() ?? '';
      const parsed = parseStatsFromResponse(rawContent, input.actionType);

      return {
        reply: parsed.reply || fallback.reply,
        stats: parsed.stats,
      };
    } finally {
      clearTimeout(timeoutId);
    }
  } catch {
    return {
      reply: fallback.reply,
      stats: fallback.stats,
    };
  }
}

function normalizeFallbackState(state: NurtureStats): NurtureStats {
  return {
    level: clampFallbackValue(state.level, 1, 99, DEFAULT_NURTURE_STATE.level),
    intimacy: clampFallbackValue(
      state.intimacy,
      0,
      100,
      DEFAULT_NURTURE_STATE.intimacy
    ),
    mood: clampFallbackValue(state.mood, 0, 100, DEFAULT_NURTURE_STATE.mood),
  };
}

function parseStatsFromResponse(content: string, actionType: NurtureActionType) {
  const match = content.match(/\[STATS\]\s*(\{[\s\S]*?\})\s*\[\/STATS\]/);
  const plainReply = content.replace(/\[STATS\][\s\S]*?\[\/STATS\]/, '').trim();

  if (!match) {
    return {
      reply: plainReply,
      stats: randomizeStats(actionType),
    };
  }

  try {
    const parsed = JSON.parse(match[1]) as {
      intimacy?: number;
      mood?: number;
    };

    return {
      reply: plainReply,
      stats: {
        intimacy: clampToActionRange(actionType, 'intimacy', parsed.intimacy),
        mood: clampToActionRange(actionType, 'mood', parsed.mood),
      },
    };
  } catch {
    return {
      reply: plainReply,
      stats: randomizeStats(actionType),
    };
  }
}

function clampToActionRange(
  actionType: NurtureActionType,
  stat: 'intimacy' | 'mood',
  value: number | undefined
) {
  const range = ITEM_RANGES[actionType][stat];
  const numericValue = Number.isFinite(value) ? Math.round(value as number) : randomInt(range[0], range[1]);
  return Math.max(range[0], Math.min(range[1], numericValue));
}

function randomizeStats(actionType: NurtureActionType) {
  const range = ITEM_RANGES[actionType];

  return {
    intimacy: randomInt(range.intimacy[0], range.intimacy[1]),
    mood: randomInt(range.mood[0], range.mood[1]),
  };
}

function calculateNextState(state: NurtureStats, stats: { intimacy: number; mood: number }) {
  const rawIntimacy = state.intimacy + stats.intimacy;
  const leveledUp = rawIntimacy >= 100;

  return {
    state: {
      level: leveledUp ? state.level + 1 : state.level,
      intimacy: leveledUp ? 0 : clampStat(rawIntimacy),
      mood: clampStat(state.mood + stats.mood),
    },
    leveledUp,
  };
}

function createFallbackReaction(
  character: Host,
  actionType: NurtureActionType,
  userContent: string
) {
  const stats = randomizeStats(actionType);

  const reply =
    actionType === 'message'
      ? `${userContent}って伝えてくれてうれしいよ。${character.displayName}は、今日もあなたの気持ちを大事に受け取ってるからね。`
      : `${ITEM_OPTIONS[actionType].label}ありがとう。${character.displayName}、なんだか心までぽかぽかしてきたよ。`;

  return { reply, stats };
}

function randomInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function clampFallbackValue(
  value: number,
  min: number,
  max: number,
  fallback: number
) {
  const numericValue = Number.isFinite(value) ? value : fallback;
  return Math.max(min, Math.min(max, numericValue));
}
