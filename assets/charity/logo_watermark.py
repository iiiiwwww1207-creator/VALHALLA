#!/usr/bin/env python3
"""4枚の図版の地に、VALHALLA のロゴを大きく透かしとして敷く。

図版（これまでの活動／当日の流れ／リターン／資金の使い道）は
どれも同じ 1774x887・SCALE=2 の作りなので、処理をここに1本化する。

ロゴ自体には手を加えない。原画の色も箔のテクスチャも形も縦横比も
そのままで、拡大と、地に馴染ませるための不透明度だけを操作する。
（色を塗り替えたり、単色に潰したりはしない）

置き方は「画面いっぱいに1つ、薄く」。小さめに濃く置くと地の上に
茶色い塊が乗ったように見え、逆に大きく薄く敷くとロゴの字が読めて
背景の模様として成立する。小さいロゴを散らすのは、背景がうるさく
なって上の文字が読めなくなるのでやらない。
"""
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
LOGO = HERE / "logo_gold.webp"


def stamp(base: Image.Image, scale: float = 0.86, opacity: int = 19,
          center: tuple[float, float] = (0.50, 0.50)) -> Image.Image:
    """base（RGBA）にロゴを透かしで敷いて返す。

    scale    … 画像の幅に対するロゴの幅の比
    opacity  … 0-255。文字の下に来るので、読みを邪魔しない濃さにする
    center   … 置く中心。画像の幅・高さに対する比で指定する
    """
    if not LOGO.exists():
        raise FileNotFoundError(f"ロゴが見つかりません: {LOGO}")

    logo = Image.open(LOGO).convert("RGBA")
    width = round(base.width * scale)
    height = round(logo.height * width / logo.width)
    logo = logo.resize((width, height), Image.Resampling.LANCZOS)

    # 元のアルファを保ったまま、全体の濃さだけを落とす
    alpha = logo.getchannel("A").point(lambda v: round(v * opacity / 255))
    logo.putalpha(alpha)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.alpha_composite(logo, (round(base.width * center[0] - width / 2),
                                 round(base.height * center[1] - height / 2)))
    return Image.alpha_composite(base.convert("RGBA"), layer)
