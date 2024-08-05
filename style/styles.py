from abc import ABCMeta, abstractmethod

from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from paint.paintables import PaintContext


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
    def __init__(self, root_folder: EntityFolder):
        self.root_folder = root_folder

    def paint_folder_dfs(self, context: PaintContext, folder: EntityFolder) -> None:
        """
        递归绘制文件夹，遇到视野之外的直接排除
        """
        # 先绘制本体
        if folder.body_shape.is_collision(context.camera.cover_world_rectangle):
            folder.paint(context)
        else:
            return
        # 递归绘制子文件夹
        for child in folder.children:
            if isinstance(child, EntityFolder):
                self.paint_folder_dfs(context, child)
            elif isinstance(child, EntityFile):
                if child.body_shape.is_collision(context.camera.cover_world_rectangle):
                    child.paint(context)

    def paint_objects(self, context: PaintContext) -> None:
        self.paint_folder_dfs(context, self.root_folder)
