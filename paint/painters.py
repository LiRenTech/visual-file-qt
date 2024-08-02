from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QTransform

from data_struct.number_vector import NumberVector

# 施工中...
class VisualFilePainter:
    def __init__(self, painter: QPainter):
        self._painter = painter

    def paint_solid_line(
        self, point1: NumberVector, point2: NumberVector, color: QColor, width: float
    ):
        pen = QPen(color, width)  # 创建QPen并设置颜色和宽度
        self._painter.setPen(pen)
        self._painter.setBrush(color)
        self._painter.setRenderHint(QPainter.Antialiasing)
        self._painter.drawLine(
            int(point1.x), int(point1.y), int(point2.x), int(point2.y)
        )
        self._painter.setPen(QColor(0, 0, 0, 0))
        self._painter.setBrush(QColor(0, 0, 0, 0))
        self._painter.setRenderHint(QPainter.Antialiasing, False)
