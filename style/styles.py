from abc import ABCMeta, abstractmethod
import math

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

    def f(self, camera_current_scale: float) -> float:
        """
        根据当前缩放比例，计算出文件夹的最大深度
        x：当前缩放比例
        放大看细节：>1
        缩小看宏观：<1
        y：当前视野能看到的文件夹深度等级，也就是函数线下面的是能看到的，上面的深度是看不到的

        """
        if camera_current_scale >= 1:
            return float("inf")
        else:
            return math.tan(camera_current_scale * (math.pi / 2)) * 10

    def _paint_folder_dfs(
        self, context: PaintContext, folder: EntityFolder, current_deep_index: int
    ) -> None:
        """
        递归绘制文件夹，遇到视野之外的直接排除
        current_deep_index 从0开始，表示当前文件夹的深度
        """
        # 看看是否因为缩放太小，视野看到的太宏观，就不绘制太细节的东西
        exclude_level = self.f(context.camera.current_scale)
        if current_deep_index != 0 and current_deep_index > exclude_level:
            print("skip folder deep index", current_deep_index)
            return
        q = context.painter.q_painter()
        # 先绘制本体
        if folder.body_shape.is_collision(context.camera.cover_world_rectangle):
            color_rate = folder.deep_level / self.folder_max_deep_index
            q.setPen(
                QPen(get_color_by_level(color_rate), 1 / context.camera.current_scale)
            )
            if (
                exclude_level < 2147483647
                and math.floor(exclude_level) == current_deep_index
            ):
                # 这时代表文件夹内部已经不显示了，要将文件夹名字居中显示在中央
                q.setFont(QFont("Consolas", int(16 / context.camera.current_scale)))
                pass
            else:
                if q.font().pointSize != 16:
                    q.setFont(QFont("Consolas", 16))
            folder.paint(context)
        else:
            return
        # 递归绘制子文件夹
        child_deep_index = current_deep_index + 1
        for child in folder.children:
            if isinstance(child, EntityFolder):
                self._paint_folder_dfs(context, child, child_deep_index)
            elif isinstance(child, EntityFile):
                if child_deep_index > self.f(context.camera.current_scale):
                    continue
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
        self._paint_folder_dfs(context, self.root_folder, 0)
        q.setPen(QColor(0, 0, 0, 0))
        q.setBrush(QColor(0, 0, 0, 0))
        q.setRenderHint(QPainter.Antialiasing, False)
