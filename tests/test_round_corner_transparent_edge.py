import unittest

from thumbor.ext.filters import _round_corner

WIDTH = 60
HEIGHT = 60
RADIUS = 20


class RoundCornerTransparentEdgeTestCase(unittest.TestCase):
    def test_opaque_pixels_are_not_darkened_by_edge_smoothing(self):
        # White RGBA picture, fill color white, transparent mode on.
        # The smoothed edge must not leave opaque pixels that are darker
        # than the white fill: that is the dark ring the issue describes.
        buf = bytes(b"\xff" * (WIDTH * HEIGHT * 4))
        out = _round_corner.apply(
            1, "RGBA", RADIUS, RADIUS, 255, 255, 255,
            WIDTH, HEIGHT, buf, 1,
        )

        dark_opaque = []
        for i in range(WIDTH * HEIGHT):
            r, g, b, a = out[i * 4:i * 4 + 4]
            if a == 255 and (r < 255 or g < 255 or b < 255):
                dark_opaque.append(i)

        self.assertEqual(
            dark_opaque,
            [],
            "opaque edge pixels darkened by round_corner transparent mode",
        )
