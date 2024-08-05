from functools import lru_cache
from PyQt5.QtGui import QColor


def mix_colors(color1, color2, rate) -> QColor:
    """
    Mixes two colors together based on a ratio.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = (1 - rate) * r1 + rate * r2
    g = (1 - rate) * g1 + rate * g2
    b = (1 - rate) * b1 + rate * b2
    return QColor(int(r), int(g), int(b))

@lru_cache(maxsize=1000)
def get_color_by_level(rate: int) -> QColor:
    """
    根据等级获取颜色
    :param level:
    :return:
    """
    return mix_colors((35, 170, 242), (76, 236, 45), rate)