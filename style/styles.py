from abc import ABCMeta, abstractmethod

from PyQt5.QtGui import QPainter, QColor, QFont, QPen

from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from paint.paintables import PaintContext
from tools.color_utils import get_color_by_level


class Styleable(metaclass=ABCMeta):
    """代表了一组Paintable的样式"""

    @abstractmethod
    def paint_objects(self, context: PaintContext) -> None:
        """使用context绘制本对象，不包括该对象的子对象

        Args:
            context (PaintContext): 待使用的context
        """
        pass


class EntityFolderDefaultStyle(Styleable):
    def __init__(self, root_folder: EntityFolder, folder_max_deep_index: int):
        """构造方法

        Args:
            root_folder (EntityFolder): 要渲染的文件夹树的根
            folder_max_deep_index (int): 文件夹最大深度
        """
        self.root_folder = root_folder
        self.folder_max_deep_index = folder_max_deep_index

    def _paint_folder_dfs(self, context: PaintContext, folder: EntityFolder) -> None:
        """
        递归绘制文件夹，遇到视野之外的直接排除
        """
        q = context.painter.q_painter()
        # 先绘制本体
        if folder.body_shape.is_collision(context.camera.cover_world_rectangle):
            color_rate = folder.deep_level / self.folder_max_deep_index
            q.setPen(
                QPen(get_color_by_level(color_rate), 1 / context.camera.current_scale)
            )
            if q.font().pointSize != 16:
                q.setFont(QFont("Consolas", 16))
            folder.paint(context)
        else:
            return
        # 递归绘制子文件夹
        for child in folder.children:
            if isinstance(child, EntityFolder):
                self._paint_folder_dfs(context, child)
            elif isinstance(child, EntityFile):
                if child.body_shape.is_collision(context.camera.cover_world_rectangle):
                    color_rate = child.deep_level / self.folder_max_deep_index
                    q.setPen(
                        QPen(
                            get_color_by_level(color_rate),
                            1 / context.camera.current_scale,
                        )
                    )
                    if q.font().pointSize != 14:
                        q.setFont(QFont("Consolas", 14))
                    child.paint(context)

    def paint_objects(self, context: PaintContext) -> None:
        q = context.painter.q_painter()
        q.setBrush(QColor(255, 255, 255, 0))
        q.setRenderHint(QPainter.Antialiasing)
        q.setFont(QFont("Consolas", 16))
        self._paint_folder_dfs(context, self.root_folder)
        q.setPen(QColor(0, 0, 0, 0))
        q.setBrush(QColor(0, 0, 0, 0))
        q.setRenderHint(QPainter.Antialiasing, False)
