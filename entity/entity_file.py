"""
文件矩形实体
"""
from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from entity.entity import Entity

from tools.string_tools import get_width_by_file_name


class EntityFile(Entity):
    """
    文件矩形
    """

    def __init__(self, location_left_top: NumberVector, full_path: str, parent):
        """
        左上角的位置
        :param location_left_top: 
        """
        full_path = full_path.replace("\\", "/")

        file_name = full_path.split("/")[-1]

        self.full_path = full_path
        self.location = location_left_top
        self.body_shape = Rectangle(location_left_top, get_width_by_file_name(file_name), 100)
        super().__init__(self.body_shape)
        # 最终用于显示的名字
        self.file_name = file_name

        self.parent = parent  # parent是EntityFolder 但会循环引入，这里就没有写类型
        pass

    def move(self, d_location: NumberVector):
        super().move(d_location)
        if not self.parent:
            return
        # 推移其他同层的矩形框
        brother_entities: list[Entity] = self.parent.children

        # d_location 经过测试发现不是0

        for entity in brother_entities:
            if entity == self:
                continue

            if self.body_shape.is_collision(entity.body_shape):
                # 如果发生了碰撞，则计算两个矩形的几何中心，被撞的矩形按照几何中心连线弹开一段距离
                # 这段距离向量的模长刚好就是d_location的模长
                self_center_location = self.body_shape.center
                entity_center_location = entity.body_shape.center
                # 碰撞方向单位向量
                d_distance = (entity_center_location - self_center_location).normalize()
                d_distance *= d_location.magnitude()
                # 弹开距离
                entity.move(d_distance)

        # 还要让父文件夹收缩调整
        self.parent.adjust()
