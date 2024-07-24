import os
import random

from data_struct.number_vector import NumberVector
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder


class FileObserver:

    def __init__(self, folder_full_path: str):
        self.folder_full_path: str = folder_full_path

        self.root_folder: EntityFolder = EntityFolder(NumberVector(0, 0), self.folder_full_path)
        # 更新树结构
        self.root_folder.update_tree_content()
        self.root_folder.adjust_tree_location()
        # self.root_folder.adjust()

        # 当前正在拖拽的
        self.dragging_entity: EntityFile | EntityFolder | None = None
        # 拖拽点相对于原点的偏移
        self.dragging_offset: NumberVector = NumberVector(0, 0)

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
        res = [self.root_folder]
        for file in folder.children:
            if isinstance(file, EntityFolder):
                res.append(file)
                res.extend(self._entity_folders(file))
        return res

    def get_entity_folders(self) -> list[EntityFolder]:
        return self._entity_folders(self.root_folder)

    def get_entity_files(self) -> list[EntityFile]:
        return self._entity_files(self.root_folder)

    def get_entity_by_location(self, location_world: NumberVector) -> EntityFile | EntityFolder | None:
        """
        判断一个点是否击中了某个实体文件
        :param location_world:
        :return:
        """
        # 优先击中文件
        for entity_file in self._entity_files(self.root_folder):
            if location_world in entity_file.body_shape:
                return entity_file
        # 其次击中文件夹
        entity_folders = self._entity_folders(self.root_folder)
        # 文件夹列表按层级深度排序，越深的在前面
        entity_folders.sort(key=lambda x: x.full_path.count("/"), reverse=True)
        print(entity_folders)
        for entity_folder in entity_folders:
            if location_world in entity_folder.body_shape:
                # print(entity_folder.full_path, "点击到了文件夹")
                return entity_folder
        # 未击中任何实体
        return None
