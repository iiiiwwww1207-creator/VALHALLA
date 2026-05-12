// ============================================================
// キャスト公開データ（クライアント用）
//
// ⚠️ このファイルだけをクライアントコンポーネントで import すること
// ⚠️ cast-list.ts は絶対に 'use client' コンポーネントで import しないこと
//
// 誕生日は含まない。
// マッチングには lifePathNumber（1〜9）を使用する。
// lifePathNumber は誕生日の各桁の合計を1桁になるまで足した値。
// 誕生日そのものはこのファイルに存在しないため、ユーザーに漏れない。
// ============================================================

export interface CastPublic {
  id: string;
  name: string;
  image: string;           // '/images/cast/xxx.jpg'  写真なしは ''
  lifePathNumber: number;  // 1〜9（マッチング用）
}

export const CAST_PUBLIC: CastPublic[] = [
  { id: 'mizuki',        name: '冬島 水月',               image: '/images/cast/mizuki.jpg',    lifePathNumber: 7 },
  { id: 'souka',         name: '爽花',                    image: '/images/cast/souka.jpg',     lifePathNumber: 3 },
  { id: 'roma',          name: '苺愛 ロマ',               image: '/images/cast/roma.jpg',      lifePathNumber: 7 },
  { id: 'tokia',         name: '時愛',                    image: '/images/cast/tokia.jpg',     lifePathNumber: 2 },
  { id: 'mafuyu',        name: '真冬',                    image: '',                           lifePathNumber: 4 },
  { id: 'mio',           name: '白夜 澪音',               image: '/images/cast/rene.jpg',      lifePathNumber: 2 },
  { id: 'sakura_ryo',    name: '桜木 凌',                 image: '/images/cast/ryo03.jpg',     lifePathNumber: 2 },
  { id: 'nagi_shiraishi',name: '白石 凪',                 image: '/images/cast/nagi01.jpg',    lifePathNumber: 5 },
  { id: 'yoeru',         name: 'ヨエル',                  image: '/images/cast/yoeru.jpg',     lifePathNumber: 5 },
  { id: 'amu',           name: '御伽 逢夢',               image: '/images/cast/amu.jpg',       lifePathNumber: 6 },
  { id: 'ryunosuke',     name: '芥川 龍之介',             image: '/images/cast/ryunosuke.jpg', lifePathNumber: 1 },
  { id: 'reon01',        name: 'れおんまん',              image: '/images/cast/reon01.jpg',    lifePathNumber: 2 },
  { id: 'chisaki',       name: '夜凪 ちさき',             image: '/images/cast/chisaki.jpg',   lifePathNumber: 5 },
  { id: 'kinari',        name: 'きなり',                  image: '/images/cast/kinari.jpg',    lifePathNumber: 2 },
  { id: 'mero',          name: '如月 メロ',               image: '',                           lifePathNumber: 9 },
  { id: 'isagi',         name: '宝樹 潔',                 image: '/images/cast/isagi.jpg',     lifePathNumber: 1 },
  { id: 'hatsuno',       name: '汐華 初流乃',             image: '',                           lifePathNumber: 3 },
  { id: 'sho01',         name: '夏海 翔',                 image: '/images/cast/sho01.jpg',     lifePathNumber: 6 },
  { id: 'ittetsu',       name: '佐伯 イッテツ',           image: '',                           lifePathNumber: 4 },
  { id: 'rion01',        name: '流川 麗音',               image: '/images/cast/rion01.jpg',    lifePathNumber: 6 },
  { id: 'tanaka',        name: '田中 彼方',               image: '/images/cast/tanaka.jpg',    lifePathNumber: 2 },
  { id: 'junon',         name: 'じゅのん',                image: '/images/cast/junon.jpg',     lifePathNumber: 3 },
  { id: 'sakura',        name: 'サクラ',                  image: '/images/cast/sakura.jpg',    lifePathNumber: 5 },
  { id: 'kirara',        name: '輝羅々',                  image: '',                           lifePathNumber: 1 },
  { id: 'osamu',         name: '太宰 治',                 image: '/images/cast/osamu.jpg',     lifePathNumber: 3 },
  { id: 'hayato',        name: '鳴瀬 隼人',               image: '/images/cast/rion.jpg',      lifePathNumber: 3 },
  { id: 'shieru',        name: '香月 シエル',             image: '/images/cast/shieru.jpg',    lifePathNumber: 2 },
  { id: 'hikawa',        name: '氷川',                    image: '/images/cast/rimuru.jpg',    lifePathNumber: 9 },
  { id: 'ryoma',         name: '優月 リョーマ',           image: '/images/cast/ryoma.jpg',     lifePathNumber: 9 },
  { id: 'minato',        name: '一ノ瀬 湊',               image: '/images/cast/minato.jpg',    lifePathNumber: 7 },
  { id: 'rain',          name: 'レイン',                  image: '/images/cast/rein.jpg',      lifePathNumber: 7 },
  { id: 'luna',          name: '紬 琉七',                 image: '/images/cast/luna.jpg',      lifePathNumber: 2 },
  { id: 'yua',           name: '月街 優愛',               image: '/images/cast/yua.jpg',       lifePathNumber: 9 },
  { id: 'ryu00',         name: '一色 緑',                 image: '/images/cast/ryu00.jpg',     lifePathNumber: 7 },
  { id: 'aren1',         name: '進撃のアレン・イェーガー', image: '/images/cast/aren1.jpg',     lifePathNumber: 8 },
  { id: 'takara01',      name: '泉 貴羅',                 image: '/images/cast/takara01.jpg',  lifePathNumber: 6 },
  { id: 'rei04',         name: '綾波 レイ',               image: '/images/cast/rei04.jpg',     lifePathNumber: 5 },
  { id: 'reito',         name: '緋景 怜斗',               image: '/images/cast/reito.jpg',     lifePathNumber: 5 },
  { id: 'omi',           name: 'OMI',                     image: '/images/cast/omi.jpg',       lifePathNumber: 7 },
  { id: 'toa',           name: '篁 十亜',                 image: '/images/cast/toa.jpg',       lifePathNumber: 1 },
  { id: 'aki',           name: '早川 アキ',               image: '/images/cast/aki.jpg',       lifePathNumber: 4 },
  { id: 'doragon',       name: '一 ドラゴン',             image: '/images/cast/doragon.jpg',   lifePathNumber: 6 },
  { id: 'hanemiya',      name: '羽宮 一虎',               image: '/images/cast/hanemiya.jpg',  lifePathNumber: 2 },
  { id: 'kaoru03',       name: '東乃 かおる',             image: '/images/cast/kaoru03.jpg',   lifePathNumber: 1 },
  { id: 'nagi',          name: '如月 凪',                 image: '/images/cast/nagi.jpg',      lifePathNumber: 1 },
  { id: 'mari',          name: '真希波 マリ',             image: '/images/cast/mari.jpg',      lifePathNumber: 8 },
  { id: 'keisuke01',     name: '場地 圭介',               image: '/images/cast/keisuke01.jpg', lifePathNumber: 8 },
  { id: 'kurama',        name: '蔵馬',                    image: '/images/cast/kurama.jpg',    lifePathNumber: 2 },
  { id: 'ukyomaru',      name: '右京 遊戯',               image: '/images/cast/ukyomaru.jpg',  lifePathNumber: 8 },
  { id: 'saki',          name: 'サキ・ゾルディック',      image: '',                           lifePathNumber: 4 },
  { id: 'kaede01',       name: '水無瀬 楓',               image: '/images/cast/kaede01.jpg',   lifePathNumber: 3 },
  { id: 'airu',          name: '黒瀬 愛依瑠',             image: '/images/cast/airu.jpg',      lifePathNumber: 7 },
  { id: 'yuki',          name: '草摩 由希',               image: '',                           lifePathNumber: 9 },
  { id: 'renya01',       name: '恋夜',                    image: '/images/cast/renya01.jpg',   lifePathNumber: 3 },
  { id: 'yato',          name: '夜ト',                    image: '/images/cast/yato.jpg',      lifePathNumber: 4 },
  { id: 'haru02',        name: '藤咲 陽',                 image: '/images/cast/haru02.jpg',    lifePathNumber: 2 },
  { id: 'kisumi',        name: '喜澄',                    image: '/images/cast/kisumi.jpg',    lifePathNumber: 7 },
  { id: 'riko',          name: '京本 リコ',               image: '/images/cast/riko.jpg',      lifePathNumber: 1 },
  { id: 'suika',         name: '酔花',                    image: '/images/cast/suika.jpg',     lifePathNumber: 8 },
  { id: 'ayato',         name: '霧嶋 絢都',               image: '/images/cast/ayato.jpg',     lifePathNumber: 3 },
  { id: 'haon',          name: 'HAON',                    image: '/images/cast/haon.jpg',      lifePathNumber: 3 },
  { id: 'ruka',          name: '三葉 るか',               image: '/images/cast/ruka.jpg',      lifePathNumber: 9 },
  { id: 'shien',         name: '玄野 紫苑',               image: '/images/cast/shien.jpg',     lifePathNumber: 1 },
  { id: 'masaki',        name: '日向 雅輝',               image: '/images/cast/masaki.jpg',    lifePathNumber: 4 },
  { id: 'shu',           name: 'SHU',                     image: '/images/cast/shu.jpg',       lifePathNumber: 1 },
  { id: 'mikoto03',      name: '御坂 美琴',               image: '/images/cast/mikoto03.jpg',  lifePathNumber: 9 },
  { id: 'mikoto04',      name: '宇崎 星羅',               image: '/images/cast/mikoto04.jpg',  lifePathNumber: 2 },
  { id: 'yu01',          name: '朝日奈 優',               image: '/images/cast/yu01.jpg',      lifePathNumber: 1 },
  { id: 'rui01',         name: '月神 ルイ',               image: '/images/cast/rui01.jpg',     lifePathNumber: 9 },
  { id: 'karuma',        name: 'カルマ',                  image: '/images/cast/karuma.jpg',    lifePathNumber: 6 },
  { id: 'maton',         name: 'マエダ・マトン',          image: '/images/cast/maton.jpg',     lifePathNumber: 9 },
  { id: 'minami01',      name: 'みなみ',                  image: '/images/cast/minami01.jpg',  lifePathNumber: 1 },
  { id: 'neruru',        name: '安蘭戯 ねるる',           image: '/images/cast/neruru.jpg',    lifePathNumber: 1 },
  { id: 'aren03',        name: '亜蓮',                    image: '/images/cast/aren03.jpg',    lifePathNumber: 7 },
  { id: 'rea01',         name: '永久 恋愛',               image: '/images/cast/rea01.jpg',     lifePathNumber: 7 },
  { id: 'ko',            name: 'KOU',                     image: '/images/cast/ko.jpg',        lifePathNumber: 7 },
];
