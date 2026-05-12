// ============================================================
// VALHALLAキャストデータ
// birthday: 'YYYY-MM-DD'
// image: '/images/cast/{id}.jpg'  ※写真未取得の場合は ''
// imageStatus:
//   'confirmed' = 名前とファイル名が確実に一致
//   'inferred'  = ファイル名の読みから推定（要確認）
//   'missing'   = 写真未取得
// ============================================================

export type ImageStatus = 'confirmed' | 'inferred' | 'missing';

export interface CastEntry {
  id: string;
  name: string;
  birthday: string;        // 'YYYY-MM-DD'
  image: string;           // '/images/cast/{id}.jpg' or ''
  imageStatus: ImageStatus;
}

export const CAST_LIST: CastEntry[] = [
  // ── 1月 ──────────────────────────────────────────
  { id: 'mizuki',       name: '冬島 水月',               birthday: '1999-01-05', image: '/images/cast/mizuki.jpg',    imageStatus: 'confirmed' },
  { id: 'souka',        name: '爽花',                    birthday: '1992-01-08', image: '/images/cast/souka.jpg',     imageStatus: 'inferred'  },
  { id: 'roma',         name: '苺愛 ロマ',               birthday: '1999-01-14', image: '/images/cast/roma.jpg',      imageStatus: 'confirmed' },
  { id: 'tokia',        name: '時愛',                    birthday: '2002-01-15', image: '/images/cast/tokia.jpg',     imageStatus: 'inferred'  },
  { id: 'mafuyu',       name: '真冬',                    birthday: '2001-01-18', image: '',                           imageStatus: 'missing'   },
  { id: 'mio',          name: '白夜 澪音',               birthday: '1998-01-19', image: '/images/cast/mio.jpg',       imageStatus: 'confirmed' },
  { id: 'sakura',       name: '桜木 凌',                 birthday: '1997-01-20', image: '/images/cast/sakura.jpg',    imageStatus: 'confirmed' },
  { id: 'nagi',         name: '白石 凪',                 birthday: '1998-01-22', image: '/images/cast/nagi.jpg',      imageStatus: 'confirmed' },
  { id: 'yoeru',        name: 'ヨエル',                  birthday: '2003-01-26', image: '/images/cast/yoeru.jpg',     imageStatus: 'inferred'  },
  { id: 'omu',          name: '御伽 逢夢',               birthday: '2002-01-28', image: '',                           imageStatus: 'missing'   },
  { id: 'ryunosuke_ak', name: '芥川 龍之介',             birthday: '2003-01-31', image: '',                           imageStatus: 'missing'   },

  // ── 2月 ──────────────────────────────────────────
  { id: 'reon01',       name: 'れおんまん',              birthday: '1999-02-17', image: '/images/cast/reon01.jpg',    imageStatus: 'confirmed' },
  { id: 'chisaki',      name: '夜凪 ちさき',             birthday: '1999-02-20', image: '/images/cast/chisaki.jpg',   imageStatus: 'confirmed' },
  { id: 'kinari',       name: 'きなり',                  birthday: '1998-02-27', image: '/images/cast/kinari.jpg',    imageStatus: 'confirmed' },
  { id: 'mero',         name: '如月 メロ',               birthday: '2005-02-27', image: '',                           imageStatus: 'missing'   },

  // ── 3月 ──────────────────────────────────────────
  { id: 'kiyoshi',      name: '宝樹 潔',                 birthday: '1992-03-13', image: '',                           imageStatus: 'missing'   },
  { id: 'hatsuno',      name: '汐華 初流乃',             birthday: '2002-03-14', image: '',                           imageStatus: 'missing'   },
  { id: 'sho01',        name: '夏海 翔',                 birthday: '2002-03-17', image: '/images/cast/sho01.jpg',     imageStatus: 'inferred'  },
  { id: 'ittetsu',      name: '佐伯 イッテツ',           birthday: '2002-03-24', image: '',                           imageStatus: 'missing'   },

  // ── 4月 ──────────────────────────────────────────
  { id: 'rein',         name: '流川 麗音',               birthday: '1998-04-02', image: '/images/cast/rein.jpg',      imageStatus: 'confirmed' },
  { id: 'tanaka',       name: '田中 彼方',               birthday: '2002-04-03', image: '/images/cast/tanaka.jpg',    imageStatus: 'confirmed' },
  { id: 'junon',        name: 'じゅのん',                birthday: '1999-04-16', image: '/images/cast/junon.jpg',     imageStatus: 'confirmed' },
  { id: 'sakura2',      name: 'サクラ',                  birthday: '2000-04-26', image: '',                           imageStatus: 'missing'   },

  // ── 5月 ──────────────────────────────────────────
  { id: 'kirara',       name: '輝羅々',                  birthday: '2003-05-09', image: '',                           imageStatus: 'missing'   },
  { id: 'osamu',        name: '太宰 治',                 birthday: '1995-05-10', image: '/images/cast/osamu.jpg',     imageStatus: 'confirmed' },
  { id: 'hayato',       name: '鳴瀬 隼人',               birthday: '1995-05-10', image: '',                           imageStatus: 'missing'   },
  { id: 'shieru',       name: '香月 シエル',             birthday: '1999-05-14', image: '/images/cast/shieru.jpg',    imageStatus: 'confirmed' },
  { id: 'hikawa',       name: '氷川',                    birthday: '2002-05-18', image: '',                           imageStatus: 'missing'   },
  { id: 'ryoma',        name: '優月 リョーマ',           birthday: '1993-05-27', image: '/images/cast/ryoma.jpg',     imageStatus: 'confirmed' },
  { id: 'minato',       name: '一ノ瀬 湊',               birthday: '1997-05-30', image: '/images/cast/minato.jpg',    imageStatus: 'confirmed' },

  // ── 6月 ──────────────────────────────────────────
  { id: 'rain',         name: 'レイン',                  birthday: '2003-06-14', image: '',                           imageStatus: 'missing'   },
  { id: 'tsunagi',      name: '紬 琉七',                 birthday: '1996-06-25', image: '',                           imageStatus: 'missing'   },

  // ── 7月 ──────────────────────────────────────────
  { id: 'yua',          name: '月街 優愛',               birthday: '1999-07-01', image: '/images/cast/yua.jpg',       imageStatus: 'confirmed' },
  { id: 'midori',       name: '一色 緑',                 birthday: '1996-07-02', image: '',                           imageStatus: 'missing'   },
  { id: 'aren03',       name: '進撃のアレン・イェーガー', birthday: '1995-07-04', image: '/images/cast/aren03.jpg',    imageStatus: 'confirmed' },
  { id: 'takara01',     name: '泉 貴羅',                 birthday: '2002-07-04', image: '/images/cast/takara01.jpg',  imageStatus: 'confirmed' },
  { id: 'rei04',        name: '綾波 レイ',               birthday: '1992-07-04', image: '/images/cast/rei04.jpg',     imageStatus: 'inferred'  },
  { id: 'reito',        name: '緋景 怜斗',               birthday: '2002-07-12', image: '/images/cast/reito.jpg',     imageStatus: 'confirmed' },
  { id: 'omi',          name: 'OMI',                     birthday: '2001-07-15', image: '/images/cast/omi.jpg',       imageStatus: 'confirmed' },
  { id: 'toa',          name: '篁 十亜',                 birthday: '2002-07-17', image: '/images/cast/toa.jpg',       imageStatus: 'confirmed' },
  { id: 'aki',          name: '早川 アキ',               birthday: '2002-07-20', image: '/images/cast/aki.jpg',       imageStatus: 'confirmed' },
  { id: 'doragon',      name: '一 ドラゴン',             birthday: '1991-07-24', image: '/images/cast/doragon.jpg',   imageStatus: 'confirmed' },
  { id: 'hanemiya',     name: '羽宮 一虎',               birthday: '2000-07-29', image: '/images/cast/hanemiya.jpg',  imageStatus: 'confirmed' },
  { id: 'kaoru03',      name: '東乃 かおる',             birthday: '1997-07-31', image: '/images/cast/kaoru03.jpg',   imageStatus: 'confirmed' },

  // ── 8月 ──────────────────────────────────────────
  { id: 'kisaragi_nagi', name: '如月 凪',                birthday: '1995-08-05', image: '',                           imageStatus: 'missing'   },
  { id: 'mari',          name: '真希波 マリ',            birthday: '2004-08-12', image: '/images/cast/mari.jpg',      imageStatus: 'confirmed' },
  { id: 'keisuke01',     name: '場地 圭介',              birthday: '1994-08-22', image: '/images/cast/keisuke01.jpg', imageStatus: 'confirmed' },
  { id: 'kurama',        name: '蔵馬',                   birthday: '1993-08-26', image: '/images/cast/kurama.jpg',    imageStatus: 'confirmed' },
  { id: 'yoeru2',        name: '右京 遊戯',              birthday: '1995-08-30', image: '',                           imageStatus: 'missing'   },

  // ── 9月 ──────────────────────────────────────────
  { id: 'saki',         name: 'サキ・ゾルディック',      birthday: '1996-09-06', image: '',                           imageStatus: 'missing'   },
  { id: 'kaede01',      name: '水無瀬 楓',               birthday: '2003-09-07', image: '/images/cast/kaede01.jpg',   imageStatus: 'confirmed' },
  { id: 'airu',         name: '黒瀬 愛依瑠',             birthday: '2002-09-30', image: '/images/cast/airu.jpg',      imageStatus: 'inferred'  },

  // ── 10月 ─────────────────────────────────────────
  { id: 'yuki',         name: '草摩 由希',               birthday: '1987-10-01', image: '',                           imageStatus: 'missing'   },
  { id: 'yoruha',       name: '恋夜',                    birthday: '1996-10-04', image: '/images/cast/yoruha.jpg',    imageStatus: 'confirmed' },
  { id: 'yato',         name: '夜ト',                    birthday: '1999-10-11', image: '/images/cast/yato.jpg',      imageStatus: 'confirmed' },
  { id: 'fujisaki',     name: '藤咲 陽',                 birthday: '1998-10-19', image: '',                           imageStatus: 'missing'   },
  { id: 'kisumi',       name: '喜澄',                    birthday: '2001-10-21', image: '/images/cast/kisumi.jpg',    imageStatus: 'confirmed' },
  { id: 'riko',         name: '京本 リコ',               birthday: '2004-10-30', image: '/images/cast/riko.jpg',      imageStatus: 'confirmed' },

  // ── 11月 ─────────────────────────────────────────
  { id: 'suika',        name: '酔花',                    birthday: '2001-11-03', image: '/images/cast/suika.jpg',     imageStatus: 'inferred'  },
  { id: 'ayato',        name: '霧嶋 絢都',               birthday: '2004-11-04', image: '/images/cast/ayato.jpg',     imageStatus: 'confirmed' },
  { id: 'haon',         name: 'HAON',                    birthday: '1999-11-09', image: '/images/cast/haon.jpg',      imageStatus: 'confirmed' },
  { id: 'ruka',         name: '三葉 るか',               birthday: '1987-11-09', image: '/images/cast/ruka.jpg',      imageStatus: 'confirmed' },
  { id: 'shien',        name: '玄野 紫苑',               birthday: '1998-11-17', image: '/images/cast/shien.jpg',     imageStatus: 'confirmed' },
  { id: 'ryunosuke',    name: '日向 雅輝',               birthday: '1997-11-21', image: '/images/cast/ryunosuke.jpg', imageStatus: 'confirmed' },
  { id: 'shu',          name: 'SHU',                     birthday: '1998-11-26', image: '/images/cast/shu.jpg',       imageStatus: 'confirmed' },
  { id: 'mikoto03',     name: '御坂 美琴',               birthday: '1997-11-26', image: '/images/cast/mikoto03.jpg',  imageStatus: 'confirmed' },

  // ── 12月 ─────────────────────────────────────────
  { id: 'uzaki',        name: '宇崎 星羅',               birthday: '2004-12-02', image: '',                           imageStatus: 'missing'   },
  { id: 'yu01',         name: '朝日奈 優',               birthday: '1998-12-07', image: '/images/cast/yu01.jpg',      imageStatus: 'confirmed' },
  { id: 'rui01',        name: '月神 ルイ',               birthday: '1988-12-07', image: '/images/cast/rui01.jpg',     imageStatus: 'confirmed' },
  { id: 'karuma',       name: 'カルマ',                  birthday: '1997-12-13', image: '/images/cast/karuma.jpg',    imageStatus: 'confirmed' },
  { id: 'maton',        name: 'マエダ・マトン',          birthday: '1986-12-18', image: '/images/cast/maton.jpg',     imageStatus: 'confirmed' },
  { id: 'minami01',     name: 'みなみ',                  birthday: '2003-12-20', image: '/images/cast/minami01.jpg',  imageStatus: 'confirmed' },
  { id: 'neruru',       name: '安蘭戯 ねるる',           birthday: '2002-12-21', image: '/images/cast/neruru.jpg',    imageStatus: 'confirmed' },
  { id: 'aren1',        name: '亜蓮',                    birthday: '2003-12-26', image: '/images/cast/aren1.jpg',     imageStatus: 'confirmed' },
  { id: 'eien',         name: '永久 恋愛',               birthday: '2000-12-29', image: '',                           imageStatus: 'missing'   },
  { id: 'ko',           name: 'KOU',                     birthday: '1990-12-30', image: '/images/cast/ko.jpg',        imageStatus: 'confirmed' },
];

// ── 集計 ──────────────────────────────────────────────────
export const CONFIRMED_COUNT = CAST_LIST.filter(c => c.imageStatus === 'confirmed').length;
export const INFERRED_COUNT  = CAST_LIST.filter(c => c.imageStatus === 'inferred').length;
export const MISSING_COUNT   = CAST_LIST.filter(c => c.imageStatus === 'missing').length;
export const TOTAL_COUNT     = CAST_LIST.length;
