import io

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_transparent_palette_gif():
    img = Image.new("P", (40, 40), 0)
    img.putpalette([0, 0, 255, 0, 0, 0] + [0, 0, 0] * 254)
    for x in range(20, 40):
        for y in range(40):
            img.putpixel((x, y), 1)
    buf = io.BytesIO()
    img.save(buf, format="GIF", transparency=1)
    return buf.getvalue()


def test_resized_gif_keeps_transparency_index():
    engine = Engine(Context(config=Config()))
    engine.load(make_transparent_palette_gif(), ".gif")
    engine.resize(20, 20)
    data = engine.read(".gif")

    result = Image.open(io.BytesIO(data))
    assert result.info.get("transparency") is not None
