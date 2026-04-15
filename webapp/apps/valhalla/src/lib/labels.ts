import type {
  ConversationStyle,
  DistanceType,
  FaceType,
  PersonalityTag,
  StyleTag,
} from '@yggdra/shared';

export const faceTypeLabels: Record<FaceType, string> = {
  korean: '韓国系',
  johnny: 'ジャニーズ系',
  wild: 'ワイルド系',
  dog: '犬系',
  cat: '猫系',
};

export const styleLabels: Record<StyleTag, string> = {
  calm: '落ち着き',
  energetic: '盛り上げ上手',
  mature: '大人の余裕',
  passionate: '情熱型',
  healing: '癒やし系',
  intellectual: '知性派',
  sweet_talker: '甘い言葉',
  big_brother: '兄貴肌',
};

export const personalityLabels: Record<PersonalityTag, string> = {
  tsundere: 'ツンデレ',
  oraora: 'オラオラ',
  healing: 'いやし',
  calm: '安心感',
  flashy: 'ギラギラ',
  adhd: 'ADHD系',
};

export const distanceLabels: Record<DistanceType, string> = {
  friend: '友達みたいに',
  elder_brother: 'お兄ちゃん距離',
  special: '特別扱い',
  equal: '対等な関係',
  adaptive: '空気で合わせる',
};

export const conversationLabels: Record<ConversationStyle, string> = {
  listener: '聞き上手',
  balanced: 'バランス型',
  talker: '話して引っ張る',
};
