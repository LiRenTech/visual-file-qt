"""
文件矩形实体
"""

from typing import Any, List
from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from data_struct.text import Text
from entity.entity import Entity

from paint.paint_utils import PainterUtils
from paint.paintables import PaintContext, Paintable
from tools.color_utils import get_color_by_level
from tools.string_tools import get_width_by_file_name
from PyQt5.QtGui import QColor


class EntityFile(Entity):
    """
    文件矩形
    """

    def __init__(
        self, location_left_top: NumberVector, full_path: str, parent: "EntityFolder"
    ):
        """
        左上角的位置
        :param location_left_top:
        """
        full_path = full_path.replace("\\", "/")

        file_name = full_path.split("/")[-1]

        self.full_path = full_path
        self.location = location_left_top
        self.deep_level = 0  # 相对深度，0表示最外层
        self.body_shape = Rectangle(
            location_left_top, get_width_by_file_name(file_name), 100
        )
        super().__init__(self.body_shape)
        # 最终用于显示的名字
        self.file_name = file_name

        self.parent = parent  # parent是EntityFolder 但会循环引入，这里就没有写类型
        pass

    def move(self, d_location: NumberVector):
        """
        文件夹移动
        """
        super().move(d_location)
        if not self.parent:
            return
        # 推移其他同层的兄弟矩形框
        brother_entities: list[Entity] = self.parent.children

        # d_location 经过测试发现不是0

        for entity in brother_entities:
            if entity == self:
                continue

            if self.body_shape.is_collision(entity.body_shape):
                self.collide_with(entity)

        # 还要让父文件夹收缩调整
        self.parent.adjust()

    def output_data(self) -> dict[str, Any]:
        return {
            "kind": "file",
            "name": self.file_name,
            "bodyShape": self.body_shape.output_data(),
        }

    def read_data(self, data: dict[str, Any]):
        if data["kind"] != "file":
            raise ValueError("kind should be file")
        if data["name"] != self.file_name:
            raise ValueError("读取的文件名不匹配", data["name"], self.file_name)

        self.body_shape.read_data(data["bodyShape"])

    def __repr__(self):
        return f"({self.file_name})"

    def get_components(self) -> List[Paintable]:
        return []

    def paint(self, context: PaintContext) -> None:
        context.painter.paint_rect(self.body_shape)
        context.painter.paint_text(
            Text(self.body_shape.location_left_top + NumberVector(5, 5), self.file_name)
        )
