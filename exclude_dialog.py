from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QCheckBox,
)

from exclude_manager import EXCLUDE_MANAGER


class ExcludeDialog(QDialog):
    """
    用于设置排除项的对话框
    """

    def __init__(self, parent=None):
        super(ExcludeDialog, self).__init__(parent)
        self.setWindowTitle("设置排除")

        layout = QVBoxLayout(self)

        # 添加一些示例控件
        # ==== 局部排除 ====
        self.local_exclude_checkbox = QCheckBox(
            "开启.gitignore文件识别自动排除功能", self
        )
        # 设置此选项的初始状态
        self.local_exclude_checkbox.setChecked(EXCLUDE_MANAGER.is_local_exclude)

        self.local_exclude_checkbox.stateChanged.connect(
            self.on_local_exclude_state_changed
        )
        print(EXCLUDE_MANAGER.is_local_exclude)
        layout.addWidget(self.local_exclude_checkbox)
        layout.addWidget(
            QLabel(
                "以上功能开启后，您如果打开了一个项目集文件夹，会自动识别每个项目文件夹中的.gitignore并排除",
                self,
            )
        )
        # ==== 全局排除 ====
        self.local_exclude_checkbox = QCheckBox("开启全局排除功能", self)
        self.local_exclude_checkbox.setChecked(EXCLUDE_MANAGER.is_global_exclude)
        self.local_exclude_checkbox.stateChanged.connect(
            self.on_global_exclude_state_changed
        )
        layout.addWidget(self.local_exclude_checkbox)
        layout.addWidget(
            QLabel("设置全局排除（以下相当于您在编写gitignore文件时使用的规则）:", self)
        )

        self.text_edit = QTextEdit(self)
        # 设置初始内容
        self.text_edit.setPlainText(EXCLUDE_MANAGER.user_input_content)
        layout.addWidget(self.text_edit)
        layout.addWidget(
            QLabel(
                "注意，如果您现在已经打开了文件，保存后需要重新“打开文件夹”才能生效",
                self,
            )
        )
        save_button = QPushButton("保存", self)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        cancel_button = QPushButton("取消", self)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def on_local_exclude_state_changed(self, state: int):
        if state == 2:  # 2 表示选中状态
            print("局部排除功能已开启")
            EXCLUDE_MANAGER.is_local_exclude = True
        else:
            print("局部排除功能已关闭")
            EXCLUDE_MANAGER.is_local_exclude = False

    def on_global_exclude_state_changed(self, state: int):
        if state == 2:  # 2 表示选中状态
            print("全局排除功能已开启")
            EXCLUDE_MANAGER.is_global_exclude = True
        else:
            print("全局排除功能已关闭")
            EXCLUDE_MANAGER.is_global_exclude = False

    def save_settings(self):
        # 获取多行文本内容
        text = self.text_edit.toPlainText()
        # 在这里处理保存逻辑，例如保存到 EXCLUDE_MANAGER
        EXCLUDE_MANAGER.update_exclude_content(text)
        self.accept()
