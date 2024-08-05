from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QTransform
from PyQt5.QtCore import QRectF, QPointF

from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle


# 施工中...
class VisualFilePainter:
    def __init__(self, painter: QPainter):
        self._painter = painter

    def painter(self) -> QPainter:
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
    
    def paint_text(self, left_top: NumberVector, text: str):
        ascent = self._painter.fontMetrics().ascent()
        self._painter.drawText(QPointF(left_top.x, left_top.y + ascent), text)
    
