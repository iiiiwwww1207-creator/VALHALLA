// ============================================================
// VALHALLAキャストデータ（完全版）
// ホスホス(host2.jp/shop/yggdrasill04/)のURLスラグと
// ユーザー提供の名前・生年月日を完全照合済み
//
// imageStatus:
//   'confirmed' = ホスホスURLスラグとファイル名が一致・確定
//   'missing'   = ホスホスにページあるが写真未ダウンロード
//   'no_page'   = ホスホスにページ自体がない
// ============================================================

export type ImageStatus = 'confirmed' | 'missing' | 'no_page';

export interface CastEntry {
  id: string;
  name: string;            // ユーザー提供の名前
  nameOnHosthos: string;   // ホスホス上の表記（差異がある場合）
  birthday: string;        // 'YYYY-MM-DD'
  image: string;           // '/images/cast/{slug}.jpg' or ''
  imageStatus: ImageStatus;
}

export const CAST_LIST: CastEntry[] = [

  // ── 1月 ──────────────────────────────────────────────────
  {
    id: 'mizuki', name: '冬島 水月', nameOnHosthos: '冬島水月',
    birthday: '1999-01-05', image: '/images/cast/mizuki.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'souka', name: '爽花', nameOnHosthos: '爽花',
    birthday: '1992-01-08', image: '/images/cast/souka.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'roma', name: '苺愛 ロマ', nameOnHosthos: '苺愛ロマ',
    birthday: '1999-01-14', image: '/images/cast/roma.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'tokia', name: '時愛', nameOnHosthos: '時愛',
    birthday: '2002-01-15', image: '/images/cast/tokia.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'mafuyu', name: '真冬', nameOnHosthos: '（ホスホス掲載なし）',
    birthday: '2001-01-18', image: '', imageStatus: 'no_page',
  },
  {
    id: 'mio', name: '白夜 澪音', nameOnHosthos: '白夜澪音',
    birthday: '1998-01-19', image: '/images/cast/rene.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rene" → rene.jpg が白夜澪音の写真
    // mio.jpg は「社美緒」という別人の写真のため注意
  },
  {
    id: 'sakura_ryo', name: '桜木 凌', nameOnHosthos: '桜木 凌',
    birthday: '1997-01-20', image: '/images/cast/ryo03.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "ryo03" → ryo03.jpg が桜木凌の写真
    // sakura.jpg は「サクラ」という別人の写真のため注意
  },
  {
    id: 'nagi_shiraishi', name: '白石 凪', nameOnHosthos: '白石 凪',
    birthday: '1998-01-22', image: '', imageStatus: 'missing',
    // ※ ホスホスのURLスラグは "nagi01" → 未ダウンロード
  },
  {
    id: 'yoeru', name: 'ヨエル', nameOnHosthos: 'ヨエル',
    birthday: '2003-01-26', image: '/images/cast/yoeru.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'amu', name: '御伽 逢夢', nameOnHosthos: '御伽逢夢',
    birthday: '2002-01-28', image: '/images/cast/amu.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ryunosuke', name: '芥川 龍之介', nameOnHosthos: '芥川 龍之介',
    birthday: '2003-01-31', image: '/images/cast/ryunosuke.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "ryunosuke"
  },

  // ── 2月 ──────────────────────────────────────────────────
  {
    id: 'reon01', name: 'れおんまん', nameOnHosthos: 'れおんまん',
    birthday: '1999-02-17', image: '/images/cast/reon01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'chisaki', name: '夜凪 ちさき', nameOnHosthos: '夜凪ちさき',
    birthday: '1999-02-20', image: '/images/cast/chisaki.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'kinari', name: 'きなり', nameOnHosthos: 'きなり',
    birthday: '1998-02-27', image: '/images/cast/kinari.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'mero', name: '如月 メロ', nameOnHosthos: '（ホスホス掲載なし）',
    birthday: '2005-02-27', image: '', imageStatus: 'no_page',
  },

  // ── 3月 ──────────────────────────────────────────────────
  {
    id: 'isagi', name: '宝樹 潔', nameOnHosthos: '宝樹潔',
    birthday: '1992-03-13', image: '/images/cast/isagi.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "isagi"
  },
  {
    id: 'hatsuno', name: '汐華 初流乃', nameOnHosthos: '汐華 初流乃',
    birthday: '2002-03-14', image: '', imageStatus: 'missing',
    // ※ ホスホスのURLスラグは "haruno" → 未ダウンロード
  },
  {
    id: 'sho01', name: '夏海 翔', nameOnHosthos: '夏海 翔',
    birthday: '2002-03-17', image: '/images/cast/sho01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ittetsu', name: '佐伯 イッテツ', nameOnHosthos: '佐伯イッテツ',
    birthday: '2002-03-24', image: '', imageStatus: 'missing',
    // ※ ホスホスのURLスラグは "ittetsu" → 未ダウンロード
  },

  // ── 4月 ──────────────────────────────────────────────────
  {
    id: 'rion01', name: '流川 麗音', nameOnHosthos: '流川麗音',
    birthday: '1998-04-02', image: '/images/cast/rion01.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rion01" → rion01.jpg が流川麗音の写真
    // rein.jpg は「レイン」という別人の写真のため注意
  },
  {
    id: 'tanaka', name: '田中 彼方', nameOnHosthos: '田中彼方',
    birthday: '2002-04-03', image: '/images/cast/tanaka.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'junon', name: 'じゅのん', nameOnHosthos: 'じゅのん',
    birthday: '1999-04-16', image: '/images/cast/junon.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'sakura', name: 'サクラ', nameOnHosthos: 'サクラ',
    birthday: '2000-04-26', image: '/images/cast/sakura.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "sakura" → sakura.jpg がサクラの写真
    // 桜木凌はryo03.jpgのため注意
  },

  // ── 5月 ──────────────────────────────────────────────────
  {
    id: 'kirara', name: '輝羅々', nameOnHosthos: '（ホスホス掲載なし）',
    birthday: '2003-05-09', image: '', imageStatus: 'no_page',
  },
  {
    id: 'osamu', name: '太宰 治', nameOnHosthos: '太宰 治',
    birthday: '1995-05-10', image: '/images/cast/osamu.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'hayato', name: '鳴瀬 隼人', nameOnHosthos: '鳴瀬隼人',
    birthday: '1995-05-10', image: '/images/cast/rion.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rion" → rion.jpg が鳴瀬隼人の写真
  },
  {
    id: 'shieru', name: '香月 シエル', nameOnHosthos: '香月シエル',
    birthday: '1999-05-14', image: '/images/cast/shieru.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'hikawa', name: '氷川', nameOnHosthos: '氷川',
    birthday: '2002-05-18', image: '/images/cast/rimuru.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rimuru" → rimuru.jpg が氷川の写真
  },
  {
    id: 'ryoma', name: '優月 リョーマ', nameOnHosthos: '優月リョーマ',
    birthday: '1993-05-27', image: '/images/cast/ryoma.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'minato', name: '一ノ瀬 湊', nameOnHosthos: '一ノ瀬 湊',
    birthday: '1997-05-30', image: '/images/cast/minato.jpg', imageStatus: 'confirmed',
  },

  // ── 6月 ──────────────────────────────────────────────────
  {
    id: 'rain', name: 'レイン', nameOnHosthos: 'レイン',
    birthday: '2003-06-14', image: '/images/cast/rein.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rein" → rein.jpg がレインの写真
    // 流川麗音はrion01.jpgのため注意
  },
  {
    id: 'luna', name: '紬 琉七', nameOnHosthos: '紬 琉七',
    birthday: '1996-06-25', image: '/images/cast/luna.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "luna"
  },

  // ── 7月 ──────────────────────────────────────────────────
  {
    id: 'yua', name: '月街 優愛', nameOnHosthos: '月街優愛',
    birthday: '1999-07-01', image: '/images/cast/yua.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ryu00', name: '一色 緑', nameOnHosthos: '一色 緑',
    birthday: '1996-07-02', image: '/images/cast/ryu00.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "ryu00"
  },
  {
    id: 'aren1', name: '進撃のアレン・イェーガー', nameOnHosthos: '進撃のアレン・イェーガー',
    birthday: '1995-07-04', image: '/images/cast/aren1.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "aren1"（亜蓮はaren03のため注意）
  },
  {
    id: 'takara01', name: '泉 貴羅', nameOnHosthos: '泉 貴羅',
    birthday: '2002-07-04', image: '/images/cast/takara01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'rei04', name: '綾波 レイ', nameOnHosthos: '彩波レイ',
    birthday: '1992-07-04', image: '/images/cast/rei04.jpg', imageStatus: 'confirmed',
    // ※ ホスホス表記は「彩波レイ」。ユーザー提供名は「綾波レイ」（漢字が異なるが同一人物）
  },
  {
    id: 'reito', name: '緋景 怜斗', nameOnHosthos: '緋景怜斗',
    birthday: '2002-07-12', image: '/images/cast/reito.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'omi', name: 'OMI', nameOnHosthos: 'OMI',
    birthday: '2001-07-15', image: '/images/cast/omi.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'toa', name: '篁 十亜', nameOnHosthos: '篁 十亜',
    birthday: '2002-07-17', image: '/images/cast/toa.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'aki', name: '早川 アキ', nameOnHosthos: '早川アキ',
    birthday: '2002-07-20', image: '/images/cast/aki.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'doragon', name: '一 ドラゴン', nameOnHosthos: '一ドラゴン',
    birthday: '1991-07-24', image: '/images/cast/doragon.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'hanemiya', name: '羽宮 一虎', nameOnHosthos: '羽宮一虎',
    birthday: '2000-07-29', image: '/images/cast/hanemiya.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'kaoru03', name: '東乃 かおる', nameOnHosthos: '東乃かおる',
    birthday: '1997-07-31', image: '/images/cast/kaoru03.jpg', imageStatus: 'confirmed',
  },

  // ── 8月 ──────────────────────────────────────────────────
  {
    id: 'nagi', name: '如月 凪', nameOnHosthos: '如月 凪',
    birthday: '1995-08-05', image: '/images/cast/nagi.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "nagi"（白石凪はnagi01のため注意）
  },
  {
    id: 'mari', name: '真希波 マリ', nameOnHosthos: '真希波マリ',
    birthday: '2004-08-12', image: '/images/cast/mari.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'keisuke01', name: '場地 圭介', nameOnHosthos: '場地圭介',
    birthday: '1994-08-22', image: '/images/cast/keisuke01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'kurama', name: '蔵馬', nameOnHosthos: '蔵馬',
    birthday: '1993-08-26', image: '/images/cast/kurama.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ukyomaru', name: '右京 遊戯', nameOnHosthos: '右京遊戯',
    birthday: '1995-08-30', image: '/images/cast/ukyomaru.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "ukyomaru"
  },

  // ── 9月 ──────────────────────────────────────────────────
  {
    id: 'saki', name: 'サキ・ゾルディック', nameOnHosthos: '（ホスホス掲載なし）',
    birthday: '1996-09-06', image: '', imageStatus: 'no_page',
  },
  {
    id: 'kaede01', name: '水無瀬 楓', nameOnHosthos: '水無瀬 楓',
    birthday: '2003-09-07', image: '/images/cast/kaede01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'airu', name: '黒瀬 愛依瑠', nameOnHosthos: '黒瀬 愛依瑠',
    birthday: '2002-09-30', image: '/images/cast/airu.jpg', imageStatus: 'confirmed',
  },

  // ── 10月 ─────────────────────────────────────────────────
  {
    id: 'yuki', name: '草摩 由希', nameOnHosthos: '（ホスホス掲載なし）',
    birthday: '1987-10-01', image: '', imageStatus: 'no_page',
  },
  {
    id: 'renya01', name: '恋夜', nameOnHosthos: '恋夜',
    birthday: '1996-10-04', image: '/images/cast/renya01.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "renya01"
    // yoruha.jpg は「よるは」という運営スタッフの写真のため注意
  },
  {
    id: 'yato', name: '夜ト', nameOnHosthos: '夜ト',
    birthday: '1999-10-11', image: '/images/cast/yato.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'haru02', name: '藤咲 陽', nameOnHosthos: '藤咲 陽',
    birthday: '1998-10-19', image: '/images/cast/haru02.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "haru02"
  },
  {
    id: 'kisumi', name: '喜澄', nameOnHosthos: '喜澄',
    birthday: '2001-10-21', image: '/images/cast/kisumi.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'riko', name: '京本 リコ', nameOnHosthos: '京本リコ',
    birthday: '2004-10-30', image: '/images/cast/riko.jpg', imageStatus: 'confirmed',
  },

  // ── 11月 ─────────────────────────────────────────────────
  {
    id: 'suika', name: '酔花', nameOnHosthos: '酔花',
    birthday: '2001-11-03', image: '/images/cast/suika.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ayato', name: '霧嶋 絢都', nameOnHosthos: '霧嶋絢都',
    birthday: '2004-11-04', image: '/images/cast/ayato.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'haon', name: 'HAON', nameOnHosthos: 'HAON',
    birthday: '1999-11-09', image: '/images/cast/haon.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'ruka', name: '三葉 るか', nameOnHosthos: '三葉るか',
    birthday: '1987-11-09', image: '/images/cast/ruka.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'shien', name: '玄野 紫苑', nameOnHosthos: '玄野紫苑',
    birthday: '1998-11-17', image: '/images/cast/shien.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'masaki', name: '日向 雅輝', nameOnHosthos: '日向雅輝',
    birthday: '1997-11-21', image: '/images/cast/masaki.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "masaki"
    // ryunosuke.jpg は「芥川龍之介」の写真のため注意
  },
  {
    id: 'shu', name: 'SHU', nameOnHosthos: 'SHU',
    birthday: '1998-11-26', image: '/images/cast/shu.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'mikoto03', name: '御坂 美琴', nameOnHosthos: '御坂美琴',
    birthday: '1997-11-26', image: '/images/cast/mikoto03.jpg', imageStatus: 'confirmed',
  },

  // ── 12月 ─────────────────────────────────────────────────
  {
    id: 'mikoto04', name: '宇崎 星羅', nameOnHosthos: '宇崎星羅',
    birthday: '2004-12-02', image: '/images/cast/mikoto04.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "mikoto04"
  },
  {
    id: 'yu01', name: '朝日奈 優', nameOnHosthos: '朝日奈 優',
    birthday: '1998-12-07', image: '/images/cast/yu01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'rui01', name: '月神 ルイ', nameOnHosthos: '月神ルイ',
    birthday: '1988-12-07', image: '/images/cast/rui01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'karuma', name: 'カルマ', nameOnHosthos: 'カルマ',
    birthday: '1997-12-13', image: '/images/cast/karuma.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'maton', name: 'マエダ・マトン', nameOnHosthos: 'マエダ･マトン',
    birthday: '1986-12-18', image: '/images/cast/maton.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'minami01', name: 'みなみ', nameOnHosthos: '（ホスホス掲載なし・独自ファイルあり）',
    birthday: '2003-12-20', image: '/images/cast/minami01.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'neruru', name: '安蘭戯 ねるる', nameOnHosthos: '安蘭戯ねるる',
    birthday: '2002-12-21', image: '/images/cast/neruru.jpg', imageStatus: 'confirmed',
  },
  {
    id: 'aren03', name: '亜蓮', nameOnHosthos: '亜蓮',
    birthday: '2003-12-26', image: '/images/cast/aren03.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "aren03"（進撃のアレンはaren1のため注意）
  },
  {
    id: 'rea01', name: '永久 恋愛', nameOnHosthos: '永久恋愛',
    birthday: '2000-12-29', image: '/images/cast/rea01.jpg', imageStatus: 'confirmed',
    // ※ ホスホスのURLスラグは "rea01"
  },
  {
    id: 'ko', name: 'KOU', nameOnHosthos: 'KØU',
    birthday: '1990-12-30', image: '/images/cast/ko.jpg', imageStatus: 'confirmed',
    // ※ ホスホス表記は「KØU」
  },
];

// ── 集計 ──────────────────────────────────────────────────
export const CONFIRMED_COUNT = CAST_LIST.filter(c => c.imageStatus === 'confirmed').length;
export const MISSING_COUNT   = CAST_LIST.filter(c => c.imageStatus === 'missing').length;
export const NO_PAGE_COUNT   = CAST_LIST.filter(c => c.imageStatus === 'no_page').length;
export const TOTAL_COUNT     = CAST_LIST.length;
