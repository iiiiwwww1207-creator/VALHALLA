// ── Host / Cast ──
export interface Host {
  id: string;
  displayName: string; // 源氏名
  birthday: string; // ISO date
  tarotIndex: number; // 0-21 (Major Arcana)
  photoUrl: string; // Valhalla: 実写, Yggdra: 2次元
  avatarUrl?: string; // Yggdra用2次元アバター

  // 見た目軸
  faceType: FaceType;
  kpopGroup?: string; // BTS系, Gドラゴン系 etc.

  // 中身軸
  primaryStyleTag: StyleTag;
  stylesTags: StyleTag[];
  personalityTags: PersonalityTag[];
  distanceType: DistanceType;
  conversationStyle: ConversationStyle;

  // プロフィール
  catchCopy: string; // 一言キャッチ
  hobbies: string[];
  musicGenres: string[];
  coreValue: string;
  gapText?: string; // 仮面と素顔の隙間テキスト
}

// 見た目 — 顔の系統
export type FaceType =
  | 'korean' // 韓国系
  | 'johnny' // ジャニーズ系
  | 'wild' // イカツい
  | 'dog' // 犬系
  | 'cat'; // 猫系

// 中身 — 接客スタイル
export type StyleTag =
  | 'calm'
  | 'energetic'
  | 'mature'
  | 'passionate'
  | 'healing'
  | 'intellectual'
  | 'sweet_talker'
  | 'big_brother';

// 中身 — 性格
export type PersonalityTag =
  | 'tsundere' // ツンデレ
  | 'oraora' // オラオラ
  | 'healing' // いやし
  | 'calm' // 安心
  | 'flashy' // ギラギラ
  | 'adhd'; // ADHD系

export type DistanceType =
  | 'friend'
  | 'elder_brother'
  | 'special'
  | 'equal'
  | 'adaptive';

export type ConversationStyle = 'listener' | 'balanced' | 'talker';

// ── 診断 ──
export interface DiagnosisAnswer {
  questionId: string;
  value: string | number;
}

export interface DiagnosisResult {
  hostId: string;
  score: number;
  matchReasons: string[];
}

// ── タロット ──
export interface TarotCard {
  index: number; // 0-21
  name: string; // 愚者, 魔術師, ...
  hostId: string;
  meaning: string;
  reversedMeaning: string;
}

export interface TarotReading {
  card: TarotCard;
  isReversed: boolean;
  message: string; // ホストからの一言
  date: string;
}

// ── 占いトーン ──
export type FortuneStyle = 'healing' | 'coaching';
// ユグドラ: healing — 「僕がいるよ」
// ヴァルハラ: coaching — 「一緒に頑張ろう」

// ── 通貨 ──
export interface ShanBalance {
  amount: number;
  lastUpdated: string;
}
