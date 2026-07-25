import type { Host, DiagnosisAnswer, DiagnosisResult, StyleTag } from './types';

export interface DiagnosisQuestion {
  id: string;
  text: string;
  type: 'select' | 'birthday' | 'scale' | 'text';
  options?: { value: string; label: string }[];
}

export type DiagnosisRoute = 'route1' | 'route2' | 'route3';

// ── 共通：顔の系統 ──────────────────────────────────────────────
const FACE_OPTIONS = [
  { value: 'dog',       label: '🐶 犬系（人懐っこそうな顔）' },
  { value: 'cat',       label: '🐱 猫系（クールでミステリアスな顔）' },
  { value: 'prince',    label: '👑 王子系（整った華やかな顔）' },
  { value: 'korean',    label: '🇰🇷 韓国系（シャープで洗練された顔）' },
  { value: 'wild',      label: '💪 ワイルド系（タトゥー・強面）' },
  { value: 'neutral',   label: '🌸 中性的・儚い系' },
  { value: 'cool',      label: '🎭 かっこいい系（俳優・渋め・大人っぽい）' },
  { value: 'cute',      label: '😄 かわいい系（癒し・弟・小動物感）' },
  { value: 'heisei',    label: '📼 平成顔（濃いめ・ギャル男っぽい・懐かしい系）' },
  { value: 'reiwa',     label: '✨ 令和顔（薄め・スッキリ・今っぽい系）' },
  { value: 'other',     label: 'その他（自由入力）' },
];

// ── ROUTE 3：簡易診断（占い系）──────────────────────────────────
export const ROUTE3_QUESTIONS: DiagnosisQuestion[] = [
  {
    id: 'birthday',
    text: 'あなたの生年月日は？',
    type: 'birthday',
  },
  {
    id: 'blood_type',
    text: 'あなたの血液型は？',
    type: 'select',
    options: [
      { value: 'A',     label: 'A型' },
      { value: 'B',     label: 'B型' },
      { value: 'O',     label: 'O型' },
      { value: 'AB',    label: 'AB型' },
      { value: 'other', label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'face_pref',
    text: '好きな顔の系統は？',
    type: 'select',
    options: FACE_OPTIONS,
  },
];

// ── ROUTE 2：ホスト初めての女の子向け ──────────────────────────
export const ROUTE2_QUESTIONS: DiagnosisQuestion[] = [
  {
    id: 'face_pref',
    text: '好きな顔の系統は？',
    type: 'select',
    options: FACE_OPTIONS,
  },
  {
    id: 'drink_vibe',
    text: 'どんな雰囲気で飲みたい？',
    type: 'select',
    options: [
      { value: 'lively',    label: 'わちゃわちゃ騒ぎながら飲みたい' },
      { value: 'relaxed',   label: 'ゆっくりまったり話しながら飲みたい' },
      { value: 'games',     label: 'みんなでゲームしながらわいわい飲みたい' },
      { value: 'stylish',   label: 'おしゃれな雰囲気でしっぽり飲みたい' },
      { value: 'vent',      label: '愚痴や悩みを聞いてもらいながら飲みたい' },
      { value: 'laugh',     label: 'ひたすら笑いながら飲みたい' },
      { value: 'serious',   label: '真面目な話もしつつ飲みたい' },
      { value: 'flow',      label: '流れに任せてなんとなく飲みたい' },
      { value: 'wild',      label: 'テンション上げてド派手に飲みたい' },
      { value: 'quiet',     label: '静かに寄り添ってもらいながら飲みたい' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'alcohol_style',
    text: 'お酒の飲み方は？',
    type: 'select',
    options: [
      { value: 'strong',     label: 'ガンガン飲める・強い方' },
      { value: 'moderate',   label: 'ほどほどに楽しく飲む' },
      { value: 'no_alcohol', label: '飲めないけど雰囲気で楽しめる' },
      { value: 'sleepy',     label: '酔うと眠くなるタイプ' },
      { value: 'hyper',      label: '酔うとテンションMAXになる' },
      { value: 'talky',      label: '酔うと喋りまくるタイプ' },
      { value: 'clingy',     label: '酔うと甘えたくなる' },
      { value: 'unchanged',  label: '酔っても基本変わらない' },
      { value: 'food',       label: '飲むより食べたい派' },
      { value: 'mood',       label: 'その日の気分によって全然違う' },
      { value: 'other',      label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'host_want',
    text: 'ホストに求めるものは？',
    type: 'select',
    options: [
      { value: 'fun',       label: 'とにかく楽しませてくれること' },
      { value: 'listen',    label: '話をちゃんと聞いてくれること' },
      { value: 'laugh',     label: '笑わせてくれること' },
      { value: 'special',   label: '特別感・優越感を与えてくれること' },
      { value: 'heal',      label: '癒してくれること' },
      { value: 'thrill',    label: '刺激や非日常感' },
      { value: 'casual',    label: '友達みたいな気楽さ' },
      { value: 'safe',      label: '一緒にいて安心できること' },
      { value: 'honest',    label: '本音で話せる関係' },
      { value: 'heartbeat', label: 'ときめかせてくれること' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'personality_pref',
    text: '好きな性格・タイプは？',
    type: 'select',
    options: [
      { value: 'mood_maker',  label: '明るくてムードメーカーな人' },
      { value: 'calm',        label: '穏やかで落ち着いた人' },
      { value: 'funny',       label: '面白くてずっと笑わせてくれる人' },
      { value: 'mysterious',  label: '掴みどころのないミステリアスな人' },
      { value: 'passionate',  label: '真っ直ぐで情熱的な人' },
      { value: 'reliable',    label: '包容力があって頼れる人' },
      { value: 'flat',        label: '友達みたいにフラットな人' },
      { value: 'senior',      label: '甘えさせてくれる年上感のある人' },
      { value: 'silly',       label: '一緒にバカやれるノリの良い人' },
      { value: 'respectful',  label: '自分のペースを尊重してくれる人' },
      { value: 'other',       label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'praise_pref',
    text: '褒められて嬉しいポイントは？',
    type: 'select',
    options: [
      { value: 'looks',      label: '顔・見た目' },
      { value: 'sense',      label: 'センス・ファッション' },
      { value: 'funny',      label: '話の面白さ' },
      { value: 'kind',       label: '気遣い・優しさ' },
      { value: 'strong',     label: '芯の強さ' },
      { value: 'aura',       label: '雰囲気・オーラ' },
      { value: 'smile',      label: '笑顔' },
      { value: 'smart',      label: '頭の良さ' },
      { value: 'fun_to_be',  label: '一緒にいて楽しいと言われること' },
      { value: 'special',    label: '特別感を感じさせてくれること' },
      { value: 'other',      label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'distance_pref',
    text: '距離感の理想は？',
    type: 'select',
    options: [
      { value: 'flat',      label: '友達みたいにフラットに接してほしい' },
      { value: 'special',   label: 'ちょっと特別扱いしてほしい' },
      { value: 'light',     label: '適度な距離感でさっぱりしてほしい' },
      { value: 'spoil',     label: '思いっきり甘えさせてほしい' },
      { value: 'my_pace',   label: 'こちらのペースに合わせてほしい' },
      { value: 'lead',      label: 'ぐいぐい引っ張ってほしい' },
      { value: 'intense',   label: '気が向いたときだけ全力で向き合ってほしい' },
      { value: 'always',    label: 'ずっと隣にいてほしい' },
      { value: 'shallow',   label: '深く踏み込まずさらっとしてほしい' },
      { value: 'natural',   label: '関係性は自然に育っていけばいい' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'down_time',
    text: '落ち込んだとき・しんどいときどうしてほしい？',
    type: 'select',
    options: [
      { value: 'listen',     label: '話を聞いてほしい' },
      { value: 'alone',      label: 'そっとしておいてほしい' },
      { value: 'laugh',      label: '笑わせてほしい' },
      { value: 'beside',     label: '何も言わず隣にいてほしい' },
      { value: 'outing',     label: '気分転換に連れ出してほしい' },
      { value: 'affirm',     label: '思いっきり肯定してほしい' },
      { value: 'empathy',    label: '解決策より共感がほしい' },
      { value: 'normal',     label: '普通に接してほしい・特別扱い不要' },
      { value: 'food',       label: '美味しいものを一緒に食べたい' },
      { value: 'encourage',  label: '励ましの言葉をかけてほしい' },
      { value: 'other',      label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'happy_moment',
    text: '嬉しかった言葉・されて嬉しかったことは？',
    type: 'select',
    options: [
      { value: 'comeback',   label: '「また来てね」と言われた' },
      { value: 'remembered', label: '名前を覚えてくれてた' },
      { value: 'noticed',    label: '細かいことを気にかけてくれた' },
      { value: 'laughed',    label: '笑わせてくれた' },
      { value: 'missed',     label: '「会いたかった」と言われた' },
      { value: 'singled_out',label: '自分だけに話しかけてくれた' },
      { value: 'complimented',label: 'さりげなく褒めてくれた' },
      { value: 'recalled',   label: '話をちゃんと覚えててくれた' },
      { value: 'natural',    label: '無理に盛り上げず自然体でいてくれた' },
      { value: 'treated',    label: '特別扱いしてくれた' },
      { value: 'other',      label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'relax_space',
    text: '一番リラックスできる空間は？',
    type: 'select',
    options: [
      { value: 'lively',    label: '笑いが絶えない賑やかな場所' },
      { value: 'quiet',     label: '静かで落ち着いた場所' },
      { value: 'small',     label: '少人数でじっくり話せる場所' },
      { value: 'music',     label: '音楽が流れてる心地いい場所' },
      { value: 'no_stress', label: '気を遣わなくていい場所' },
      { value: 'free_talk', label: '好きなことを話せる場所' },
      { value: 'someone',   label: '誰かがそばにいるだけでいい場所' },
      { value: 'food',      label: 'おいしいものがある場所' },
      { value: 'smiles',    label: '笑顔が多い場所' },
      { value: 'my_pace',   label: '自分のペースでいられる場所' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
];

// ── ROUTE 1：ホスクラ慣れてる女の子向け ─────────────────────────
export const ROUTE1_QUESTIONS: DiagnosisQuestion[] = [
  {
    id: 'face_pref',
    text: '好きな顔の系統は？',
    type: 'select',
    options: FACE_OPTIONS,
  },
  {
    id: 'drink_vibe',
    text: 'どんな雰囲気で飲みたい？',
    type: 'select',
    options: [
      { value: 'lively',    label: 'わちゃわちゃ騒ぎながら飲みたい' },
      { value: 'relaxed',   label: 'ゆっくりまったり話しながら飲みたい' },
      { value: 'games',     label: 'みんなでゲームしながらわいわい飲みたい' },
      { value: 'vent',      label: '愚痴や悩みを聞いてもらいながら飲みたい' },
      { value: 'laugh',     label: 'ひたすら笑いながら飲みたい' },
      { value: 'serious',   label: '真面目な話もしつつ飲みたい' },
      { value: 'flow',      label: '流れに任せてなんとなく飲みたい' },
      { value: 'wild',      label: 'テンション上げてド派手に飲みたい' },
      { value: 'quiet',     label: '静かに寄り添ってもらいながら飲みたい' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'host_want',
    text: '担当に求めるものは？',
    type: 'select',
    options: [
      { value: 'fun',       label: 'とにかく楽しませてくれること' },
      { value: 'listen',    label: '話をちゃんと聞いてくれること' },
      { value: 'laugh',     label: '笑わせてくれること' },
      { value: 'special',   label: '自分だけ特別扱いしてくれること' },
      { value: 'heal',      label: '癒してくれること' },
      { value: 'thrill',    label: '非日常感・刺激をくれること' },
      { value: 'casual',    label: '友達みたいな気楽さ' },
      { value: 'honest',    label: '本音で話せる関係' },
      { value: 'heartbeat', label: 'ときめかせてくれること' },
      { value: 'understand',label: '自分のことを深く理解してくれること' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'style_pref',
    text: '好きな接客スタイルは？',
    type: 'select',
    options: [
      { value: 'aggressive',  label: 'ぐいぐい来てくれる・積極的な子' },
      { value: 'adaptive',    label: 'こちらのペースに合わせてくれる子' },
      { value: 'flat',        label: '友達みたいにフラットに話せる子' },
      { value: 'mysterious',  label: '掴みどころのないミステリアスな子' },
      { value: 'energetic',   label: '笑いを絶やさず場を盛り上げてくれる子' },
      { value: 'caring',      label: '甘えさせてくれる・包んでくれる子' },
      { value: 'deep',        label: '話を深く聞いてくれる子' },
      { value: 'gap',         label: 'オンとオフのギャップがある子' },
      { value: 'memory',      label: '自分のことをよく覚えてくれてる子' },
      { value: 'eye_contact', label: '目を見てちゃんと話してくれる子' },
      { value: 'other',       label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'line_style',
    text: '担当とのLINEどうしてる？',
    type: 'select',
    options: [
      { value: 'daily',       label: '毎日やり取りしてる' },
      { value: 'visit_only',  label: '来店前後だけ連絡する' },
      { value: 'reply_fast',  label: '担当から来たらすぐ返す' },
      { value: 'anxious',     label: '既読スルーされると気になる' },
      { value: 'light',       label: 'あっさりしたやり取りが好き' },
      { value: 'call',        label: '電話もしたい' },
      { value: 'meet',        label: 'LINEより会って話したい派' },
      { value: 'content',     label: '連絡頻度より内容の濃さが大事' },
      { value: 'no_contact',  label: '担当とは連絡取り合わない派' },
      { value: 'other',       label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'visit_style',
    text: 'どんな通い方が自分に合ってる？',
    type: 'select',
    options: [
      { value: 'weekly',      label: '週1以上ペースで通いたい' },
      { value: 'monthly',     label: '月2〜3回ゆったり通いたい' },
      { value: 'events',      label: 'イベントのときだけ行く' },
      { value: 'spontaneous', label: '気が向いたときにふらっと行く' },
      { value: 'solo',        label: 'ひとりで全然行ける' },
      { value: 'friends',     label: '友達と一緒じゃないと行かない' },
      { value: 'loyal',       label: '担当ができたら定期的に通いたい' },
      { value: 'free',        label: '担当はいらない・フリーで気ままに通う' },
      { value: 'explore',     label: 'いろんな店を開拓しながら回るタイプ' },
      { value: 'all_in',      label: '一つの店にどっぷりはまるタイプ' },
      { value: 'other',       label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'decide_factor',
    text: '担当を決める決め手は？',
    type: 'select',
    options: [
      { value: 'first_look',  label: '第一印象・顔' },
      { value: 'vibe',        label: '話してみたときのフィーリング' },
      { value: 'remembered',  label: '自分のことを覚えてくれてるか' },
      { value: 'line',        label: 'LINEの返し方・文面' },
      { value: 'care',        label: 'さりげない気遣い' },
      { value: 'laugh',       label: '笑わせてくれるかどうか' },
      { value: 'gap',         label: 'ギャップを感じたとき' },
      { value: 'friends',     label: '友達や周りの反応' },
      { value: 'instinct',    label: 'なんとなく直感' },
      { value: 'natural',     label: '長く話してみて自然に決まった' },
      { value: 'other',       label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'long_term',
    text: '一番長く続いた担当はどんな人だった？',
    type: 'select',
    options: [
      { value: 'funny',     label: 'とにかく話が面白くて笑わせてくれた' },
      { value: 'memory',    label: '自分の話をちゃんと覚えててくれた' },
      { value: 'distance',  label: '程よい距離感が心地よかった' },
      { value: 'gap',       label: 'ギャップがあってどんどんハマっていった' },
      { value: 'casual',    label: '友達みたいに気楽に話せた' },
      { value: 'special',   label: '特別扱いしてくれてる感があった' },
      { value: 'safe',      label: '一緒にいると安心できた' },
      { value: 'line',      label: 'LINEが途切れなかった' },
      { value: 'still',     label: '今も通ってる' },
      { value: 'none',      label: 'まだ長く続いた担当がいない' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'change_reason',
    text: '担当を変えたくなったきっかけは？',
    type: 'select',
    options: [
      { value: 'new_one',   label: '新しく気になる子ができた' },
      { value: 'bored',     label: 'なんとなく飽きてきた' },
      { value: 'mismatch',  label: '話が合わなくなってきた気がした' },
      { value: 'friend',    label: '友達に紹介された子が好みだった' },
      { value: 'vibe_off',  label: '相手の自分への熱量が変わった気がした' },
      { value: 'no_change', label: 'まだ変えたことがない' },
      { value: 'no_tanto',  label: 'そもそも担当を作らない' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
  {
    id: 'ideal_relation',
    text: '担当との理想の関係性は？',
    type: 'select',
    options: [
      { value: 'flat',      label: '友達みたいにフラットでいたい' },
      { value: 'special',   label: '特別な存在として見てほしい' },
      { value: 'light',     label: '適度な距離感でさっぱりしてたい' },
      { value: 'spoil',     label: '思いっきり甘えられる関係がいい' },
      { value: 'honest',    label: 'お互い本音で話せる関係' },
      { value: 'outside',   label: '店の外でも繋がっていたい' },
      { value: 'inside',    label: '店の中だけの特別な空間として楽しみたい' },
      { value: 'long',      label: '長く深く付き合っていきたい' },
      { value: 'natural',   label: '関係性は自然に育っていけばいい' },
      { value: 'flexible',  label: 'その時々で変わっていい' },
      { value: 'other',     label: 'その他（自由入力）' },
    ],
  },
];

// ルートごとの質問を取得
export function getQuestionsByRoute(route: DiagnosisRoute): DiagnosisQuestion[] {
  switch (route) {
    case 'route1': return ROUTE1_QUESTIONS;
    case 'route2': return ROUTE2_QUESTIONS;
    case 'route3': return ROUTE3_QUESTIONS;
  }
}

// レガシー互換（既存コードが DIAGNOSIS_QUESTIONS を使っている場合）
export const DIAGNOSIS_QUESTIONS = ROUTE2_QUESTIONS;

// ── マッチングスコア計算 ──────────────────────────────────────────
export function calculateMatch(answers: DiagnosisAnswer[], host: Host): DiagnosisResult {
  let score = 0;
  const matchReasons: string[] = [];

  for (const answer of answers) {
    switch (answer.questionId) {
      case 'face_pref': {
        const faceMap: Record<string, string> = {
          dog: 'dog', cat: 'cat', prince: 'johnny', korean: 'korean', wild: 'wild',
        };
        if (faceMap[answer.value as string] === host.faceType) {
          score += 30;
          matchReasons.push('顔のタイプがぴったり！');
        }
        break;
      }
      case 'style_pref':
      case 'drink_vibe': {
        if (answer.value === host.primaryStyleTag) {
          score += 35;
          matchReasons.push('接客スタイルが最高の相性');
        } else if (host.stylesTags.includes(answer.value as StyleTag)) {
          score += 18;
          matchReasons.push('接客スタイルの相性が良い');
        }
        break;
      }
      case 'host_want':
      case 'personality_pref': {
        if (host.personalityTags.some((t) => t === answer.value)) {
          score += 25;
          matchReasons.push('性格の相性バッチリ');
        }
        break;
      }
      case 'distance_pref':
      case 'ideal_relation': {
        if (answer.value === host.distanceType || host.distanceType === 'adaptive') {
          score += 20;
          matchReasons.push('距離感がちょうどいい');
        }
        break;
      }
      case 'birthday': {
        score += 10;
        matchReasons.push('運命の星が導いている');
        break;
      }
      case 'blood_type': {
        score += 8;
        matchReasons.push('血液型の相性が出た');
        break;
      }
    }
  }

  const maxScore = 30 + 35 + 25 + 20 + 10 + 8;
  const normalizedScore = Math.round((score / maxScore) * 100);

  return { hostId: host.id, score: normalizedScore, matchReasons };
}

export function getTopMatches(
  answers: DiagnosisAnswer[],
  hosts: Host[],
  count = 3
): DiagnosisResult[] {
  return hosts
    .map((host) => calculateMatch(answers, host))
    .sort((a, b) => b.score - a.score)
    .slice(0, count);
}
