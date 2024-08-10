from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPainter

from data_struct.rectangle import Rectangle
from data_struct.text import Text


# 施工中...
class VisualFilePainter:
    def __init__(self, painter: QPainter):
        self._painter = painter

    def q_painter(self) -> QPainter:
        return self._painter

    def paint_rect(self, rect: Rectangle):
        self._painter.drawRect(
            QRectF(
                rect.location_left_top.x,
                rect.location_left_top.y,
                rect.width,
                rect.height,
            )
        )

    def paint_text(self, text: Text):
        ascent = self._painter.fontMetrics().ascent()
        self._painter.drawText(
            QPointF(text.left_top.x, text.left_top.y + ascent), text.text
        )
