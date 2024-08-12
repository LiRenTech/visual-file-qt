from data_struct.number_vector import NumberVector
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder


class FileObserver:

    def __init__(self):
        """
        初始化文件观察者
        """
        self.folder_full_path: str = ""
        self.folder_max_deep_index = 0 + 1  # 当前最深的深度，用于渲染颜色

        self.root_folder: EntityFolder | None = None
        # 当前正在拖拽的
        self.dragging_entity: EntityFile | EntityFolder | None = None
        # 拖拽点相对于原点的偏移
        self.dragging_offset: NumberVector = NumberVector(0, 0)
        # 当前选中的实体是否是激活状态
        self.dragging_entity_activating: bool = True
        # 是否锁定拖拽
        self.is_drag_locked: bool = False

    def set_drag_lock(self, is_lock: bool):
        self.is_drag_locked = is_lock
        if is_lock:
            self.dragging_entity_activating = False

    def update_file_path(self, new_path: str):
        """
        更新文件路径，相当于外界用户换了一个想要查看的文件夹
        被外界更换文件夹的地方调用
        :param new_path:
        :return:
        """

        self.folder_full_path = new_path
        self.root_folder = EntityFolder(NumberVector(0, 0), self.folder_full_path)
        # 时间花费较少
        print("读取文件夹内容中")
        self.root_folder.update_tree_content()
        print("生成排列结构中")
        # 时间花费较大
        self.root_folder.adjust_tree_location()

        self.dragging_entity = None
        # 还需要将新的文件夹移动到世界坐标的中心。
        target_location_left_top = NumberVector(0, 0) - NumberVector(
            self.root_folder.body_shape.width / 2,
            self.root_folder.body_shape.height / 2,
        )
        self.root_folder.move_to(target_location_left_top)
        print("计算最大深度中")
        self.folder_max_deep_index = self.root_folder.count_deep_level()

    def output_layout_dict(self) -> dict:
        """
        输出当前文件夹的布局文件
        :return:
        """
        if self.root_folder is None:
            return {"layout": []}
        return {"layout": [self.root_folder.output_data()]}

    def read_layout_dict(self, layout_file: dict):
        """
        读取布局文件，恢复当前文件夹的布局
        :param layout_file:
        :return:
        """
        if self.root_folder is None:
            return
        self.root_folder.read_data(layout_file["layout"][0])
        self.dragging_entity = None

    def _entity_files(self, folder: EntityFolder) -> list[EntityFile]:
        """
        获取某个文件夹下所有的文件，包括子文件夹的文件，展平成一个列表
        :param folder:
        :return:
        """
        res = []
        for file in folder.children:
            if isinstance(file, EntityFile):
                res.append(file)
            elif isinstance(file, EntityFolder):
                res.extend(self._entity_files(file))
        return res

    def _entity_folders(self, folder: EntityFolder) -> list[EntityFolder]:
        """
        获取某个文件夹下所有的文件夹，包括子文件夹的文件夹，展平成一个列表
        :param folder:
        :return:
        """

        assert self.root_folder
        res = [self.root_folder]
        for file in folder.children:
            if isinstance(file, EntityFolder):
                res.append(file)
                res.extend(self._entity_folders(file))
        return res

    def get_entity_by_location(
        self, location_world: NumberVector
    ) -> EntityFile | EntityFolder | None:
        """
        判断一个点是否击中了某个实体文件
        :param location_world:
        :return:
        """
        if self.root_folder is None:
            return None

        return self._get_entity_by_location_dfs(location_world, self.root_folder)

    def _get_entity_by_location_dfs(
        self, location_world: NumberVector, currentEntity: EntityFile | EntityFolder
    ) -> EntityFile | EntityFolder | None:
        """递归的实现"""
        # 当前没有点到东西
        if not currentEntity.body_shape.is_contain_point(location_world):
            return None

        if isinstance(currentEntity, EntityFile):
            # 是文件
            return currentEntity
        elif isinstance(currentEntity, EntityFolder):
            # 是文件夹

            # 如果当前文件夹内部隐藏了，则直接返回当前文件夹
            if currentEntity.is_hide_inner:
                return currentEntity

            # 看看是不是击中了内部的东西
            for child in currentEntity.children:
                if isinstance(child, EntityFile):
                    # 是否击中文件
                    if child.body_shape.is_contain_point(location_world):
                        return child

                elif isinstance(child, EntityFolder):
                    # 是否击中文件夹
                    res = self._get_entity_by_location_dfs(location_world, child)
                    if res is not None:
                        return res

            # 未击中任何内部的东西，则返回当前文件夹
            return currentEntity
        else:
            raise ValueError("Unknown entity type")
