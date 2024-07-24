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
