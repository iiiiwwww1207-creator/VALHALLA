export type NurtureItemType = 'snack' | 'present' | 'training' | 'champagne';
export type NurtureActionType = NurtureItemType | 'message';
export type NurtureMessageRole = 'user' | 'character';

export interface NurtureStats {
  level: number;
  intimacy: number;
  mood: number;
}

export interface NurtureChatMessage {
  id: string;
  role: NurtureMessageRole;
  actionType: NurtureActionType | 'reply';
  content: string;
  createdAt: string;
}

export interface NurtureGetResponse {
  state: NurtureStats;
  messages: NurtureChatMessage[];
  databaseAvailable: boolean;
}

export interface NurturePostResponse extends NurtureGetResponse {
  appliedStats: {
    intimacy: number;
    mood: number;
  };
  leveledUp: boolean;
}

export const DEFAULT_NURTURE_STATE: NurtureStats = {
  level: 1,
  intimacy: 0,
  mood: 60,
};

export const OSHI_FALLBACK_STATE: NurtureStats = {
  level: 1,
  intimacy: 12,
  mood: 68,
};

export const ITEM_OPTIONS: Record<
  NurtureItemType,
  { icon: string; label: string; logLabel: string }
> = {
  snack: {
    icon: '🍰',
    label: 'おやつ',
    logLabel: 'おやつを渡した',
  },
  present: {
    icon: '🎁',
    label: 'プレゼント',
    logLabel: 'プレゼントを渡した',
  },
  training: {
    icon: '🎤',
    label: '練習',
    logLabel: '一緒に練習した',
  },
  champagne: {
    icon: '🍾',
    label: 'シャンパン',
    logLabel: 'シャンパンで乾杯した',
  },
};

export const ACTION_ICON: Record<NurtureActionType | 'reply', string> = {
  snack: ITEM_OPTIONS.snack.icon,
  present: ITEM_OPTIONS.present.icon,
  training: ITEM_OPTIONS.training.icon,
  champagne: ITEM_OPTIONS.champagne.icon,
  message: '💬',
  reply: '✨',
};

export function clampStat(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function getMoodLabel(mood: number) {
  if (mood >= 85) return 'とてもごきげん';
  if (mood >= 65) return 'ごきげん';
  if (mood >= 40) return 'おだやか';
  if (mood >= 20) return 'ちょっぴり元気待ち';
  return 'しょんぼり';
}

export function getLevelProgress(level: number) {
  return Math.max(8, Math.min(100, level * 12));
}

export function getItemPromptLabel(actionType: NurtureActionType, message?: string) {
  if (actionType === 'message') {
    return message?.trim() || '話しかけた';
  }

  return ITEM_OPTIONS[actionType].logLabel;
}
