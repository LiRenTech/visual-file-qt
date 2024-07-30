"""
排除项管理器
单例模式，全局唯一实例
"""

_init_content = """.git
__pycache__
.idea
"""


class ExcludeManager:
    def __init__(self):
        # 用户初始化输入的东西，可以看成是.gitignore文件的内容
        self.user_input_content = _init_content

        # 是否开启局部排除
        self.is_local_exclude = True
        # 是否开启全局排除
        self.is_global_exclude = True

    def update_exclude_content(self, content: str):
        self.user_input_content = content

    @property
    def exclude_list(self):
        """
        排除项列表
        """
        result = self.user_input_content.split()
        # 去掉空白项
        result = [item for item in result if item]
        # 可能还有其他的排除

        return result

    def is_file_in_global_exclude(self, file_path: str):
        """
        判断某一个文件是否应该被全局排除
        拿到的路径在上游保证 反斜杠替换为正斜杠
        """

        if not self.is_global_exclude:
            return False

        # 这里先写简单一些，暂时不支持正则表达式
        file_name = file_path.split("/")[-1]
        if file_name in self.exclude_list:
            return True
        return False

    pass


EXCLUDE_MANAGER = ExcludeManager()
del ExcludeManager
