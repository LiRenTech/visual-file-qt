from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from data_struct.text import Text
from entity.entity import Entity
from entity.entity_file import EntityFile
from paint.paintables import PaintContext, Paintable
from tools.gitignore_parser import parse_gitignore
from tools.string_tools import get_width_by_file_name
from typing import List, Optional, Any
from tools.rectangle_packing import (
    sort_rectangle_all_files,
    sort_rectangle_greedy,
    sort_rectangle_many_files_less_folders,
)
from exclude_manager import EXCLUDE_MANAGER


class EntityFolder(Entity):
    """
    文件夹矩形
    """

    PADDING = 50

    # 通用排除的文件夹
    exclusion_list = [
        ".git",  # gitignore文件本身不排除.git文件夹，所以这里强制排除
        "__pycache__",  # 貌似出了一些bug parse_gitignore 没有排除这个文件夹
        ".idea",
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
        # 不仅，要让文件夹这个框框本身移动
        super().move(d_location)
        # 还要，移动文件夹内所有实体也移动
        for child in self.children:
            # 移动自己内部所有实体的时候，也不能用move函数本身，会炸开花。
            # child.move(d_location)
            child.move_to(child.body_shape.location_left_top + d_location)

        # 推移其他同层的矩形框
        if not self.parent:
            return

        # 让父文件夹收缩调整
        self.parent.adjust()

        brother_entities: list[EntityFile | EntityFolder] = self.parent.children

        for entity in brother_entities:
            if entity == self:
                continue

            if self.body_shape.is_collision(entity.body_shape):
                self.collide_with(entity)  # FIXME: 这里无穷递归了

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
        max_deep_level = 1
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
        try:
            # 输入一个匹配函数，如果匹配则返回True，否则返回False
            matches_function = lambda _: False

            if EXCLUDE_MANAGER.is_local_exclude:
                # 在遍历之前先看看是否有.gitignore文件
                gitignore_file_path = os.path.join(
                    self.full_path, ".gitignore"
                ).replace("\\", "/")

                if os.path.exists(gitignore_file_path):
                    try:
                        matches_function = parse_gitignore(gitignore_file_path)
                    except UnicodeDecodeError:
                        # 这个不会再发生了，因为已经将这个第三方库放到本地并修改了代码了
                        print(f"文件{gitignore_file_path}编码错误，跳过")

            # 遍历文件夹内所有文件
            for file_name_sub in os.listdir(self.full_path):
                full_path_sub = os.path.join(self.full_path, file_name_sub).replace(
                    "\\", "/"
                )
                # 全局排除
                if EXCLUDE_MANAGER.is_file_in_global_exclude(full_path_sub):
                    continue
                # 局部排除
                if matches_function(full_path_sub):
                    continue

                is_have = self._is_have_child(file_name_sub)

                # 开始添加
                if os.path.isdir(full_path_sub):
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
        except PermissionError:
            # 权限不足，跳过
            # 这里或许未来可以加一种禁止访问的矩形，显示成灰色
            pass
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
        for brother_entity in self.parent.children:
            if brother_entity == self:
                continue
            if self.body_shape.is_collision(brother_entity.body_shape):
                self.collide_with(brother_entity)

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
        if len(folder.children) < 100:
            sort_strategy_function = sort_rectangle_greedy
        else:
            if all(isinstance(child, EntityFolder) for child in folder.children) or all(
                isinstance(child, EntityFile) for child in folder.children
            ):
                # 如果全是文件夹或者全是文件，按照正常的矩形排列
                sort_strategy_function = sort_rectangle_all_files
            else:
                sort_strategy_function = sort_rectangle_many_files_less_folders

        sorted_rectangle_list = sort_strategy_function(
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

    def get_components(self) -> List[Paintable]:
        return []

    def paint(self, context: PaintContext) -> None:
       context.painter.paint_rect(self.body_shape)
       context.painter.paint_text(Text(self.body_shape.location_left_top, self.folder_name))
