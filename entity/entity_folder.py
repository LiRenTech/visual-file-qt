from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from entity.entity import Entity
from entity.entity_file import EntityFile
from tools.string_tools import get_width_by_file_name
from typing import Optional, Any
from tools.rectangle_packing import sort_rectangle_greedy


class EntityFolder(Entity):
    """
    文件夹矩形
    """

    PADDING = 50

    # 通用排除的文件夹
    exclusion_list = [
        "__pycache__",
        ".git",
        ".idea",
        "node_modules",
        "dist",
        "build",
        "venv",
        ".venv" "env",
        "temp",
        ".vscode",
        "migrations",  # 数据库迁移文件
        "logs",  # 日志文件
        "cache",  # 缓存文件
    ]

    def __init__(self, location_left_top: NumberVector, full_path: str):

        full_path = full_path.replace("\\", "/")
        folder_name = full_path.split("/")[-1]

        self.full_path = full_path
        self.location = location_left_top
        self.folder_name = folder_name
        self.deep_level = 0  # 相对深度。最顶层为0
        self.body_shape = Rectangle(
            location_left_top, get_width_by_file_name(folder_name) * 2, 500
        )
        super().__init__(self.body_shape)
        # 属性节点关系
        self.parent: Optional["EntityFolder"] = None
        self.children: "list[EntityFolder | EntityFile]" = []

        # 这个矩形有点麻烦，它可能应该是一个动态变化的东西，不应该变的是它的左上角位置，变得是他的大小
        self.adjust()

    def output_data(self) -> dict[str, Any]:
        """
        递归的输出数据，最终返回一个字典
        :return:
        """
        return {
            "kind": "directory",
            "name": self.folder_name,
            "bodyShape": self.body_shape.output_data(),
            "children": [child.output_data() for child in self.children],
        }

    def read_data(self, data: dict[str, Any]):
        """
        读取数据 直接导致文件夹更新布局位置信息
        :param data:
        :return:
        """
        if data["kind"] != "directory":
            raise ValueError("kind should be directory")
        if data["name"] != self.folder_name:
            raise ValueError("读取的文件名不匹配", data["name"], self.folder_name)
        # 可以是先序遍历
        # 先更新内容
        self.body_shape.read_data(data["bodyShape"])
        # ===
        for child in self.children:
            if isinstance(child, EntityFolder):
                for data_child in data["children"]:
                    if child.folder_name == data_child["name"]:
                        child.read_data(data_child)
                        break
                else:
                    # 没找到，说明有布局文件缺失，或者文件是新增的。
                    # 将这个对齐到当前的左上角
                    child.move_to(self.body_shape.location_left_top)
                    pass
            elif isinstance(child, EntityFile):
                for data_child in data["children"]:
                    if child.file_name == data_child["name"]:
                        child.read_data(data_child)
                        break
                else:
                    child.move_to(self.body_shape.location_left_top)
                    pass

        pass

    def move(self, d_location: NumberVector):
        # 不仅，要让文件夹本身移动
        super().move(d_location)
        # 还要，移动文件夹内所有实体
        for child in self.children:
            # 移动自己内部所有实体的时候，也不能用move函数本身，会炸开花。
            # child.move(d_location)
            child.move_to(child.body_shape.location_left_top + d_location)

        # 推移其他同层的矩形框 TODO: 此处有点重复代码
        if not self.parent:
            return

        # 让父文件夹收缩调整
        self.parent.adjust()

        # ==== 开始同层碰撞检测

        brother_entities: list[EntityFile | EntityFolder] = self.parent.children

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
                # entity.move(d_distance)  # 这一弹，是造成碰撞、其他物体位置连续炸开花的罪魁祸首。
                entity.move_to(entity.body_shape.location_left_top + d_distance)

    def move_to(self, location_left_top: NumberVector):
        """
        此代码不会被用户直接拖拽调用
        :param location_left_top:
        :return:
        """
        # 移动文件夹内所有实体
        for child in self.children:
            relative_location = (
                child.body_shape.location_left_top - self.body_shape.location_left_top
            )
            # 这本身实际上是一个递归函数了
            child.move_to(location_left_top + relative_location)
        # 移动文件夹本身
        super().move_to(location_left_top)

    def _is_have_child(self, child_name: str):
        """
        判断自身文件夹内部第一层是否含有某个子文件或文件夹
        :param child_name:
        :return:
        """
        for child in self.children:
            if isinstance(child, EntityFolder):
                if child.folder_name == child_name:
                    return True
            elif isinstance(child, EntityFile):
                if child.file_name == child_name:
                    return True
            else:
                raise ValueError("子节点类型错误", child)
        return False

    def count_deep_level(self) -> int:
        """
        计算文件夹的深度
        :return:
        """
        if not self.children:
            return 1
        max_deep_level = 0
        for child in self.children:
            if isinstance(child, EntityFolder):
                deep_level = child.count_deep_level() + 1
                max_deep_level = max(max_deep_level, deep_level)
        return max_deep_level

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
            is_have = self._is_have_child(file_name_sub)

            # 开始添加
            if os.path.isdir(full_path_sub):
                # 排除的文件夹名字
                if file_name_sub in self.exclusion_list:
                    continue
                if is_have:
                    # 还要继续深入检查这个文件夹内部是否有更新
                    for chile in self.children:
                        if (
                            isinstance(chile, EntityFolder)
                            and chile.folder_name == file_name_sub
                        ):
                            # 找到这个原有的子文件夹并递归下去
                            chile.update_tree_content()
                            break
                else:
                    # 新增了一个文件夹
                    child_folder = EntityFolder(put_location, full_path_sub)
                    put_location += NumberVector(500, 0)  # 往右放

                    child_folder.parent = self
                    child_folder.deep_level = self.deep_level + 1

                    self.children.append(child_folder)
                    child_folder.update_tree_content()  # 递归调用
            else:
                if is_have:
                    continue
                # 是一个文件
                child_file = EntityFile(put_location, full_path_sub, self)
                put_location = NumberVector(0, 120)  # 往下放

                child_file.parent = self
                child_file.deep_level = self.deep_level + 1

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
            right_bound = max(
                right_bound,
                child.body_shape.location_left_top.x + child.body_shape.width,
            )
            top_bound = min(top_bound, child.body_shape.location_left_top.y)
            bottom_bound = max(
                bottom_bound,
                child.body_shape.location_left_top.y + child.body_shape.height,
            )

        self.body_shape.location_left_top = NumberVector(
            left_bound - self.PADDING, top_bound - self.PADDING
        )
        self.body_shape.width = right_bound - left_bound + self.PADDING * 2
        self.body_shape.height = bottom_bound - top_bound + self.PADDING * 2
        if not self.parent:
            return

        # 扩张的边可能会导致兄弟元素发生变化
        # 猛一想以为最多只有两个边会发生变化，但实际上由于推移多个元素的效果，可能会导致发生很复杂的变化
        # 所以每个边都要检测
        # TODO:

        # 向上调用
        self.parent.adjust() if self.parent else None
        pass

    def adjust_tree_location(self):
        """
        提供给外界调用
        :return:
        """
        self._adjust_tree_dfs(self)

    def _adjust_tree_dfs(self, folder: "EntityFolder"):
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

        # 调整当前文件夹里的所有实体顺序位置

        rectangle_list = [child.body_shape for child in folder.children]
        sorted_rectangle_list = sort_rectangle_greedy(
            [rectangle.clone() for rectangle in rectangle_list], self.PADDING
        )

        # ===
        # 先检查一下排序策略函数是否顺序正确
        if len(sorted_rectangle_list) != len(rectangle_list):
            print("排序策略错误，前后数组不相等")

        for i, rect in enumerate(rectangle_list):
            if (
                sorted_rectangle_list[i].width != rect.width
                or sorted_rectangle_list[i].height != rect.height
            ):
                print("排序策略错误")
        # ===

        for i, child in enumerate(folder.children):
            child.move_to(
                sorted_rectangle_list[i].location_left_top
                + self.body_shape.location_left_top
            )

        folder.adjust()
        pass

    def __repr__(self):
        return f"({self.full_path})"

    pass
