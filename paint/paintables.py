from abc import ABCMeta, abstractmethod
from typing import List
from PyQt5.QtGui import QPainter


class PaintContext:
    """绘制上下文，该类是为了便于在绘制时传递一些额外信息。"""

    def __init__(self, painter: QPainter):
        """
        Args:
            painter (QPainter): 已经使用QTransform将世界坐标转化为视野渲染坐标的painter
        """
        self.painter = painter


class Paintable(metaclass=ABCMeta):
    """代表了所有能绘制的一个对象，实现类通常应该依赖注入一个camera"""

    @abstractmethod
    def children() -> List["Paintable"]:
        pass

    @abstractmethod
    def paint(context: PaintContext) -> None:
        """使用context绘制本对象，不包括该对象的子对象

        Args:
            context (PaintContext): 待使用的context
        """
        pass

    