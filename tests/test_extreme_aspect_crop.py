from types import SimpleNamespace

from thumbor.point import FocalPoint
from thumbor.transformer import Transformer


class RecordingEngine:
    def __init__(self, size):
        self.size = size
        self.crops = []
        self.resizes = []

    def crop(self, left, top, right, bottom):
        self.crops.append((left, top, right, bottom))

    def resize(self, width, height):
        self.resizes.append((width, height))


def test_auto_crop_for_wide_short_target_keeps_at_least_one_pixel():
    # A 1x1 source asked for 50x25 has a 2:1 target ratio. The crop height
    # rounds to 0, which leaves an empty crop box.
    engine = RecordingEngine((1, 1))
    context = SimpleNamespace(request=SimpleNamespace(engine=engine))
    transformer = Transformer(context)
    transformer.target_width = 50.0
    transformer.target_height = 25.0
    transformer.focal_points = [
        FocalPoint.from_alignment("center", "middle", 1, 1)
    ]

    transformer.auto_crop()

    left, top, right, bottom = engine.crops[-1]
    assert right > left
    assert bottom > top


def test_fit_in_1x1_request_returns_a_real_picture():
    # issue #4: /unsafe/fit-in/1x1/940x2.png returned a 500 error page.
    # The fit-in math rounds the 2px side to 0px, which is not a picture.
    engine = RecordingEngine((940, 2))
    request = SimpleNamespace(
        engine=engine,
        adaptive=False,
        full=False,
        width=1,
        height=1,
        fit_in=True,
    )
    transformer = Transformer(SimpleNamespace(request=request))
    transformer.target_width = 1.0
    transformer.target_height = 1.0

    transformer.fit_in_resize()

    width, height = engine.resizes[-1]
    assert width >= 1
    assert height >= 1


def test_fit_in_width_only_request_returns_a_real_picture():
    # issue #4: /unsafe/fit-in/100x0/940x2.png returned a 500 error page.
    # The height for a 100px wide request from 940x2 rounds down to 0px.
    engine = RecordingEngine((940, 2))
    request = SimpleNamespace(
        engine=engine,
        adaptive=False,
        full=False,
        width=100,
        height=0,
        fit_in=True,
    )
    transformer = Transformer(SimpleNamespace(request=request))
    transformer.target_width = 100.0
    transformer.target_height = 0.0

    transformer.fit_in_resize()

    width, height = engine.resizes[-1]
    assert width >= 1
    assert height >= 1
