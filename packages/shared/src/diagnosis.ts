import type { Host, DiagnosisAnswer, DiagnosisResult, FaceType, StyleTag } from './types';

export interface DiagnosisQuestion {
  id: string;
  text: string;
  type: 'select' | 'birthday' | 'scale';
  options?: { value: string; label: string }[];
}

// 共通診断質問（両アプリで使用）
export const DIAGNOSIS_QUESTIONS: DiagnosisQuestion[] = [
  {
    id: 'birthday',
    text: 'あなたの誕生日は？',
    type: 'birthday',
  },
  {
    id: 'face_pref',
    text: '好みの顔のタイプは？',
    type: 'select',
    options: [
      { value: 'korean', label: '韓国系（BTS・BIGBANG系）' },
      { value: 'johnny', label: 'ジャニーズ系' },
      { value: 'wild', label: 'ワイルド・イカツい系' },
      { value: 'dog', label: '犬系（人懐っこい）' },
      { value: 'cat', label: '猫系（ミステリアス）' },
    ],
  },
  {
    id: 'style_pref',
    text: 'どんな接客が好き？',
    type: 'select',
    options: [
      { value: 'healing', label: '癒やし系・安心できる' },
      { value: 'energetic', label: '盛り上げてくれる' },
      { value: 'intellectual', label: '知的な会話がしたい' },
      { value: 'sweet_talker', label: '甘い言葉で酔わせてほしい' },
      { value: 'big_brother', label: '頼れるお兄さん' },
    ],
  },
  {
    id: 'personality_pref',
    text: 'どんな性格に惹かれる？',
    type: 'select',
    options: [
      { value: 'tsundere', label: 'ツンデレ' },
      { value: 'oraora', label: 'オラオラ系' },
      { value: 'healing', label: 'いやし系' },
      { value: 'calm', label: '安心系' },
      { value: 'flashy', label: 'ギラギラ系' },
    ],
  },
  {
    id: 'distance_pref',
    text: 'どんな距離感が心地いい？',
    type: 'select',
    options: [
      { value: 'friend', label: '友達みたいに気軽に' },
      { value: 'elder_brother', label: 'お兄ちゃんみたいに守ってほしい' },
      { value: 'special', label: '特別な存在として扱ってほしい' },
      { value: 'equal', label: '対等に話したい' },
    ],
  },
  {
    id: 'conversation_pref',
    text: '会話ではどっちがいい？',
    type: 'select',
    options: [
      { value: 'listener', label: '聞き上手な人がいい' },
      { value: 'talker', label: 'たくさん話してくれる人がいい' },
      { value: 'balanced', label: 'バランスよく' },
    ],
  },
];

// マッチングスコア計算
export function calculateMatch(answers: DiagnosisAnswer[], host: Host): DiagnosisResult {
  let score = 0;
  const matchReasons: string[] = [];

  for (const answer of answers) {
    switch (answer.questionId) {
      case 'face_pref':
        if (answer.value === host.faceType) {
          score += 30;
          matchReasons.push('顔のタイプがぴったり！');
        }
        break;

      case 'style_pref':
        if (answer.value === host.primaryStyleTag) {
          score += 38; // primary_style_tag: +35〜40
          matchReasons.push('接客スタイルが最高の相性');
        } else if (host.stylesTags.includes(answer.value as StyleTag)) {
          score += 18; // secondary: +15〜20
          matchReasons.push('接客スタイルの相性が良い');
        }
        break;

      case 'personality_pref':
        if (host.personalityTags.some((t) => t === answer.value)) {
          score += 25;
          matchReasons.push('性格の相性バッチリ');
        }
        break;

      case 'distance_pref':
        if (answer.value === host.distanceType || host.distanceType === 'adaptive') {
          score += 20;
          matchReasons.push('距離感がちょうどいい');
        }
        break;

      case 'conversation_pref':
        if (answer.value === host.conversationStyle || host.conversationStyle === 'balanced') {
          score += 15;
          matchReasons.push('会話のテンポが合う');
        }
        break;

      case 'birthday': {
        // Simple zodiac compatibility (placeholder)
        score += 10;
        matchReasons.push('運命の星が導いている');
        break;
      }
    }
  }

  // Normalize to 0-100
  const maxScore = 30 + 38 + 25 + 20 + 15 + 10; // 138
  const normalizedScore = Math.round((score / maxScore) * 100);

  return {
    hostId: host.id,
    score: normalizedScore,
    matchReasons,
  };
}

// トップ3マッチを取得
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
