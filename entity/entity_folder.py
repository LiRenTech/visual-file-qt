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
        # 还要让父文件夹收缩调整
        if self.parent:
            self.parent.adjust()

    def move_to(self, location_left_top: NumberVector):
        # 移动文件夹内所有实体
        for child in self.children:
            relative_location = child.body_shape.location_left_top - self.body_shape.location_left_top
            # 这本身实际上是一个递归函数了
            child.move_to(location_left_top + relative_location)
        # 移动文件夹本身
        super().move_to(location_left_top)

    def update_tree_content(self):
        """
        更新文件夹树结构内容，不更新显示位置大小
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
                child_folder.update_tree_content()  # 递归调用
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

    def adjust(self):
        """
        调整文件夹框框的宽度和长度，扩大或缩进，使得将子一层文件都直观上包含进来
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

    def adjust_tree_location(self):
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

        # === 递归部分
        for child in folder.children:
            if isinstance(child, EntityFolder):
                # 是文件夹，继续递归
                self._adjust_tree_dfs(child)
        # ===
        if not isinstance(folder, EntityFolder):
            return

        # 调整当前文件夹里的所有实体顺序位置
        # 暂时采取竖着放的策略

        current_y = folder.body_shape.location_left_top.y + self.PADDING
        for child in folder.children:
            # 顶部对齐，不能直接修改位置来对齐，因为如果是一个文件夹，会导致它的子文件脱离了位置。
            child.move_to(NumberVector(
                folder.body_shape.location_left_top.x + self.PADDING,
                current_y
            ))
            current_y += child.body_shape.height + self.PADDING

        # rectangle_list = [child.body_shape for child in folder.children]
        # sorted_rectangle_list = sort_rectangle(rectangle_list, self.PADDING)
        # for (i, child) in enumerate(folder.children):
        #     child.move_to(sorted_rectangle_list[i].location_left_top)

        folder.adjust()
        pass

    def __repr__(self):
        return f"EntityFolder({self.full_path})"

    pass


def sort_rectangle(rectangles: list[Rectangle], margin: float) -> list[Rectangle]:
    """
    装箱问题，排列矩形
    :param rectangles: N个矩形的大小和位置
    :param margin: 矩形之间的间隔（为了美观考虑）
    :return: 调整好后的N个矩形的大小和位置，数组内每个矩形一一对应。
    例如：
    rectangles = [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(10, 10), 1, 1)]
    这两个矩形对角放，外套矩形空隙面积过大，空间浪费，需要调整位置。

    调整后返回：

    [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(12, 0), 1, 1)]
    参数 margin = 2
    横向放置，减少了空间浪费。
    """
    pass
