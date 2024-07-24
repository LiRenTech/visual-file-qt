from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from entity.entity import Entity
from entity.entity_file import EntityFile
from tools.string_tools import get_width_by_file_name
from typing import Optional


class EntityFolder(Entity):
    """
    文件夹矩形
    """
    PADDING = 50

    # 通用排除的文件夹
    exclusion_list = ["__pycache__", ".git", ".idea", "node_modules", "dist", "build", "venv", "env", "temp", ".vscode"]

    def __init__(self, location_left_top: NumberVector, full_path: str):
        full_path = full_path.replace("\\", "/")
        folder_name = full_path.split("/")[-1]

        self.full_path = full_path
        self.location = location_left_top
        self.folder_name = folder_name
        self.body_shape = Rectangle(location_left_top, get_width_by_file_name(folder_name) * 2, 500)
        super().__init__(self.body_shape)
        # 属性节点关系
        self.parent: Optional['EntityFolder'] = None
        self.children: list['EntityFolder' | EntityFile] = []

        # 这个矩形有点麻烦，它可能应该是一个动态变化的东西，不应该变的是它的左上角位置，变得是他的大小
        self.adjust()

    def move(self, d_location: NumberVector):
        # 不仅，要让文件夹本身移动
        super().move(d_location)
        # 还要，移动文件夹内所有实体
        for child in self.children:
            child.move(d_location)

    def update_tree(self):
        """
        更新文件夹树结构内容，只读取
        但是是递归的
        :return:
        """
        import os
        # 如果是一个文件夹，往右放
        # 如果是一个文件，往下放

        # 放置点位
        put_location = self.body_shape.location_left_top + NumberVector(0, 100)

        for file_name_sub in os.listdir(self.full_path):
            full_path_sub = os.path.join(self.full_path, file_name_sub)
            if os.path.isdir(full_path_sub):
                # 排除的文件夹名字
                if file_name_sub in self.exclusion_list:
                    continue

                # 又是一个子文件夹
                child_folder = EntityFolder(
                    put_location,
                    full_path_sub
                )
                put_location += NumberVector(500, 0)  # 往右放

                child_folder.parent = self

                self.children.append(child_folder)
                child_folder.update_tree()  # 递归调用
            else:
                # 是一个文件
                child_file = EntityFile(
                    put_location,
                    full_path_sub,
                    self
                )
                put_location = NumberVector(0, 120)  # 往下放

                child_file.parent = self

                self.children.append(child_file)
        pass

    def move_by_drag(self, new_location: NumberVector):
        self.location = new_location

    def adjust(self):
        """
        调整文件夹框框的宽度和长度
        该调整过程是相对于文件树形结构 自底向上的
        :return:
        """
        if not self.children:
            # 如果没有子节点，不调整，因为可能会导致有无穷大位置的出现
            return

        left_bound = float("inf")
        right_bound = -float("inf")
        top_bound = float("inf")
        bottom_bound = -float("inf")

        for child in self.children:
            left_bound = min(left_bound, child.body_shape.location_left_top.x)
            right_bound = max(right_bound, child.body_shape.location_left_top.x + child.body_shape.width)
            top_bound = min(top_bound, child.body_shape.location_left_top.y)
            bottom_bound = max(bottom_bound, child.body_shape.location_left_top.y + child.body_shape.height)

        self.body_shape.location_left_top = NumberVector(left_bound - self.PADDING, top_bound - self.PADDING)
        self.body_shape.width = right_bound - left_bound + self.PADDING * 2
        self.body_shape.height = bottom_bound - top_bound + self.PADDING * 2

        # 向上调用
        self.parent.adjust() if self.parent else None
        pass

    def adjust_tree(self):
        """
        提供给外界调用
        :return:
        """
        self._adjust_tree_dfs(self)

    def _adjust_tree_dfs(self, folder: 'EntityFolder'):
        """
        递归调整文件夹树形结构位置
        应该是一个后根遍历的过程，tips：这种多叉树不存在中序遍历，只有先序和后序。
        :param folder:
        :return:
        """

        # ===
        for child in folder.children:
            if isinstance(child, EntityFolder):
                # 是文件夹，继续递归
                self._adjust_tree_dfs(child)
        # ===

        # 调整当前文件夹里的所有实体顺序位置
        # 暂时采取竖着放的策略
        current_y = folder.body_shape.location_left_top.y + self.PADDING
        for child in folder.children:
            child.body_shape.location_left_top = NumberVector(folder.body_shape.location_left_top.x, current_y)
            current_y += child.body_shape.height + self.PADDING
            # child.adjust()  # 这一行可能有点多余
        pass

    def __repr__(self):
        return f"EntityFolder({self.full_path})"

    pass
