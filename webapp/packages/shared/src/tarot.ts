import type { TarotCard } from './types';

// 大アルカナ22枚 = 22人のホスト
export const TAROT_CARDS: Omit<TarotCard, 'hostId'>[] = [
  { index: 0, name: '愚者', meaning: '自由と冒険の始まり', reversedMeaning: '無計画な行動に注意' },
  { index: 1, name: '魔術師', meaning: '新しい可能性を切り開く力', reversedMeaning: '自信過剰に注意' },
  { index: 2, name: '女教皇', meaning: '直感を信じて', reversedMeaning: '考えすぎに注意' },
  { index: 3, name: '女帝', meaning: '豊かさと愛に満ちた日', reversedMeaning: '甘えすぎに注意' },
  { index: 4, name: '皇帝', meaning: 'リーダーシップを発揮する時', reversedMeaning: '支配的にならないで' },
  { index: 5, name: '教皇', meaning: '信頼できる人からの助言', reversedMeaning: '自分の判断も大切に' },
  { index: 6, name: '恋人', meaning: '運命的な出会いの予感', reversedMeaning: '迷いがあるなら立ち止まって' },
  { index: 7, name: '戦車', meaning: '勝利への意志で進め', reversedMeaning: '暴走に注意' },
  { index: 8, name: '力', meaning: '内なる強さが目覚める', reversedMeaning: '無理は禁物' },
  { index: 9, name: '隠者', meaning: '自分と向き合う大切な時間', reversedMeaning: '孤立しすぎないで' },
  { index: 10, name: '運命の輪', meaning: '転機が訪れる', reversedMeaning: '変化を恐れないで' },
  { index: 11, name: '正義', meaning: '公正な判断ができる日', reversedMeaning: '偏見に注意' },
  { index: 12, name: '吊るされた男', meaning: '視点を変えると答えが見える', reversedMeaning: '犠牲になりすぎないで' },
  { index: 13, name: '死神', meaning: '終わりと新しい始まり', reversedMeaning: '過去に囚われないで' },
  { index: 14, name: '節制', meaning: 'バランスが大切な日', reversedMeaning: '極端な行動に注意' },
  { index: 15, name: '悪魔', meaning: '誘惑に負けない強さ', reversedMeaning: '束縛から解放される' },
  { index: 16, name: '塔', meaning: '衝撃の先に真実がある', reversedMeaning: '変化を受け入れて' },
  { index: 17, name: '星', meaning: '希望の光が差す', reversedMeaning: '理想と現実のギャップに注意' },
  { index: 18, name: '月', meaning: '不安の裏に答えがある', reversedMeaning: '恐れを手放して' },
  { index: 19, name: '太陽', meaning: '最高にハッピーな日！', reversedMeaning: 'はしゃぎすぎに注意' },
  { index: 20, name: '審判', meaning: '過去の努力が報われる', reversedMeaning: '後悔よりも前を見て' },
  { index: 21, name: '世界', meaning: '全てが一つになる完成の時', reversedMeaning: '完璧を求めすぎないで' },
];

export function drawDailyTarot(userId: string, date: string): { cardIndex: number; isReversed: boolean } {
  // Simple deterministic draw based on userId + date
  const seed = `${userId}-${date}`;
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = ((hash << 5) - hash + seed.charCodeAt(i)) | 0;
  }
  const cardIndex = Math.abs(hash) % 22;
  const isReversed = Math.abs(hash >> 8) % 3 === 0; // ~33% chance reversed
  return { cardIndex, isReversed };
}
