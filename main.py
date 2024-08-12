import json
import traceback

from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import (
    QPainter,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
    QColor,
    QIcon,
    QPaintEvent,
    QDesktopServices,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QAction,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QPushButton,
)

from camera import Camera
from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from entity.entity import Entity
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from exclude_dialog import ExcludeDialog
from file_observer import FileObserver, InteractiveState
from file_openner import open_file
from paint.paint_elements import (
    paint_grid,
    paint_file_rect,
    paint_folder_rect,
    paint_details_data,
    paint_rect_in_world,
    paint_selected_rect,
    paint_alert_message,
)
from paint.paintables import PaintContext
from paint.painters import VisualFilePainter
from style.styles import EntityFolderDefaultStyle
from tools.threads import OpenFolderThread

from assets import assets

# 是为了引入assets文件夹中的资源文件，看似是灰色的没有用，但实际不能删掉
# 只是为了让pyinstaller打包时能打包到exe文件中。
# 需要进入assets文件夹后在命令行输入指令 `pyrcc5 image.rcc -o assets.py` 来更新assets.py文件


class Canvas(QMainWindow):

    def __init__(self):
        super().__init__()

        self._open_folder_thread = None
        self.init_ui()

        # 重要对象绑定
        self.camera = Camera(NumberVector.zero(), 1920, 1080)
        self.file_observer = FileObserver()

        # 创建一个定时器用于定期更新窗口
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(16)  # 1000/60 大约= 16ms
        # 启动定时器
        self.timer.start()

        # 窗口移动相关
        self._last_mouse_move_location = NumberVector.zero()  # 注意这是一个世界坐标
        # 是否正在更新布局
        self._is_updating_layout = False
        # 是否正在打开文件夹
        self._is_open_folder = False  # 没有起到效果

    def init_ui(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle("VisualFile 大型文件夹直观可视化工具")

        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon(":/favicon.ico"))
        self._move_window_to_center()

        # 创建菜单栏
        menubar = self.menuBar()
        assert menubar
        # 创建 "文件夹" 菜单
        folder_menu = menubar.addMenu("文件夹")
        assert folder_menu
        # 创建 "Open" 菜单项
        open_action = QAction("打开文件夹", self)
        open_action.setShortcut("Ctrl+O")
        folder_menu.addAction(open_action)
        open_action.triggered.connect(self.on_open)

        # 创建 "Update" 菜单项
        update_action = QAction("更新文件夹", self)
        update_action.setShortcut("Ctrl+U")
        folder_menu.addAction(update_action)
        update_action.triggered.connect(self.on_update)

        # 创建 设置排除 菜单项
        exclude_action = QAction("设置排除", self)
        exclude_action.setShortcut("Ctrl+E")
        folder_menu.addAction(exclude_action)
        exclude_action.triggered.connect(self.show_exclude_dialog)

        # “布局”菜单
        layout_menu = menubar.addMenu("布局")
        assert layout_menu
        # 创建 "Save" 菜单项
        save_action = QAction("导出布局文件", self)
        save_action.setShortcut("Ctrl+S")
        layout_menu.addAction(save_action)
        save_action.triggered.connect(self.on_save)
        # 创建 导入 菜单项
        import_action = QAction("导入布局文件并更新布局", self)
        import_action.setShortcut("Ctrl+I")
        layout_menu.addAction(import_action)
        import_action.triggered.connect(self.on_import)

        drag_lock = QAction("锁定拖拽", self)
        drag_lock.setShortcut("Ctrl+L")
        layout_menu.addAction(drag_lock)
        drag_lock.triggered.connect(lambda: self.file_observer.set_drag_lock(True))

        drag_unlock = QAction("解锁拖拽", self)
        drag_unlock.setShortcut("Ctrl+U")
        layout_menu.addAction(drag_unlock)
        drag_unlock.triggered.connect(lambda: self.file_observer.set_drag_lock(False))

        # "视野" 菜单
        view_menu = menubar.addMenu("视野")
        assert view_menu
        # 创建 "Reset" 菜单项
        reset_action = QAction("重置缩放", self)
        reset_action.setShortcut("Ctrl+0")
        view_menu.addAction(reset_action)
        reset_action.triggered.connect(self.on_reset_zoom)

        # 创建 "快速档缩放" 菜单项
        camera_fast_mode = QAction("快速档缩放", self)
        camera_fast_mode.setShortcut("Ctrl++")
        view_menu.addAction(camera_fast_mode)
        camera_fast_mode.triggered.connect(lambda: self.camera.set_fast_mode())

        camera_slow_mode = QAction("慢速档缩放", self)
        camera_slow_mode.setShortcut("Ctrl+-")
        view_menu.addAction(camera_slow_mode)
        camera_slow_mode.triggered.connect(lambda: self.camera.set_slow_mode())

        camera_open_animation = QAction("开启动画", self)
        camera_open_animation.setShortcut("Ctrl+A")
        view_menu.addAction(camera_open_animation)
        camera_open_animation.triggered.connect(
            lambda: self.camera.set_scale_animation(True)
        )

        camera_close_animation = QAction("关闭动画", self)
        camera_close_animation.setShortcut("Ctrl+D")
        view_menu.addAction(camera_close_animation)
        camera_close_animation.triggered.connect(
            lambda: self.camera.set_scale_animation(False)
        )

        # 创建帮助说明菜单项
        help_menu = menubar.addMenu("帮助")
        assert help_menu
        help_action = QAction("帮助说明", self)
        help_action.setShortcut("Ctrl+H")
        help_menu.addAction(help_action)
        help_action.triggered.connect(self.on_help)

        pass

    def _move_window_to_center(self):
        # 获取屏幕可用空间（macOS上会有titlebar占据一部分空间）
        screen_geometry = QDesktopWidget().availableGeometry()

        # 计算新的宽度和高度（长宽各取屏幕的百分之八十）
        new_width = screen_geometry.width() * 0.8
        new_height = screen_geometry.height() * 0.8

        # 计算窗口应该移动到的新位置
        new_left = (screen_geometry.width() - new_width) / 2
        new_top = (screen_geometry.height() - new_height) / 2 + screen_geometry.top()

        # 移动窗口到新位置
        self.setGeometry(int(new_left), int(new_top), int(new_width), int(new_height))

    def show_exclude_dialog(self):
        dialog = ExcludeDialog(self)
        dialog.exec_()

    @staticmethod
    def on_help():
        # 创建一个消息框
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon("assets/favicon.ico"))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("visual-file 帮助说明")
        msg_box.setText(
            "\n\n".join(
                [
                    "框选拖拽：拖拽框选，起始点位置决定了在哪个文件夹内进行框选，框选后的矩形会变成绿色",
                    "摆放位置：按住绿色的矩形左键拖拽",
                    "打开文件：左键双击某矩形，以系统默认方式打开对应文件或文件夹",
                    "移动视野：鼠标中键拖拽 或 右键拖拽 或 WASD键",
                    "缩放视野：鼠标滚轮",
                    "重置视野：双击鼠标中键",
                    "反馈问题：如有问题建议在github上提交issues，或在b站视频下方评论区留言。",
                ]
            )
        )
        # github按钮
        button_github = QPushButton("Github 项目地址")
        msg_box.addButton(button_github, QMessageBox.ActionRole)
        button_github.clicked.connect(Canvas.__open_github)
        msg_box.setStandardButtons(QMessageBox.Ok)
        # b站按钮
        button_bilibili = QPushButton("bilibili 视频介绍")
        msg_box.addButton(button_bilibili, QMessageBox.ActionRole)
        button_bilibili.clicked.connect(Canvas.__open_bilibili)

        # 显示消息框
        msg_box.exec_()

    @staticmethod
    def __open_github():
        QDesktopServices.openUrl(QUrl("https://github.com/LiRenTech/visual-file-qt"))

    @staticmethod
    def __open_bilibili():
        QDesktopServices.openUrl(QUrl("https://www.bilibili.com/video/BV1qw4m1k7LD"))

    def on_open_folder_finish_slot(self):
        self._is_open_folder = False
        self.camera.reset()
        self.camera.target_scale = 0.1

    def on_open(self):
        # 直接读取文件
        directory = QFileDialog.getExistingDirectory(self, "选择要直观化查看的文件夹")

        if directory:
            # paint_alert_message(painter, self.camera, "请先打开文件夹")
            self._is_open_folder = True
            self._open_folder_thread = OpenFolderThread(self.file_observer, directory)
            self._open_folder_thread.finished.connect(self.on_open_folder_finish_slot)
            self._open_folder_thread.start()
            # self.file_observer.update_file_path(directory)
            # self._is_open_folder = False

        pass

    def on_save(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存布局文件", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            # 如果用户选择了文件并点击了保存按钮
            # 保存布局文件
            layout: dict = self.file_observer.output_layout_dict()

            # 确保文件扩展名为 .json
            if not file_path.endswith(".json"):
                file_path += ".json"

            with open(file_path, "w") as f:
                json.dump(layout, f)
        else:
            # 如果用户取消了保存操作
            print("Save operation cancelled.")

    def on_update(self):
        if self.file_observer.root_folder is None:
            return
        # BUG：新增的东西可能会导致父文件夹形状炸开散架
        # 更新文件夹内容
        self.file_observer.root_folder.update_tree_content()
        self.file_observer.folder_max_deep_index = (
            self.file_observer.root_folder.count_deep_level()
        )
        pass

    def on_import(self):
        # 显示文件打开对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入布局文件", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            # 如果用户选择了文件并点击了打开按钮
            # 在这里编写导入文件的逻辑
            with open(file_path, "r") as f:
                layout_dict = json.load(f)

            try:
                self._is_updating_layout = True
                self.file_observer.read_layout_dict(layout_dict)
                self._is_updating_layout = False
            except Exception as e:
                traceback.print_exc()
                print(e)
        else:
            # 如果用户取消了打开操作
            print("Import operation cancelled.")

    def on_reset_zoom(self):
        self.camera.reset()

    def tick(self):
        self.camera.tick()
        # 重绘窗口
        self.update()
        for entity in self.file_observer.dragging_entity_list:
            # 对比当前选中的实体矩形和视野矩形
            if self.camera.cover_world_rectangle.is_contain(entity.body_shape):
                # 套住了
                self.file_observer.dragging_entity_activating = True
            else:
                # 没套住
                self.file_observer.dragging_entity_activating = False
                break

    def paintEvent(self, a0: QPaintEvent | None):
        assert a0 is not None
        painter = QPainter(self)

        # 获取窗口的尺寸
        rect = self.rect()
        # 更新camera大小，防止放大窗口后缩放中心点还在左上部分
        self.camera.reset_view_size(rect.width(), rect.height())

        # 使用黑色填充整个窗口
        painter.fillRect(rect, QColor(0, 0, 0, 255))
        # 画网格
        paint_grid(painter, self.camera)

        if self._is_updating_layout:
            paint_alert_message(painter, self.camera, "正在更新布局，请稍后...")
            return
        if self._is_open_folder:
            paint_alert_message(painter, self.camera, "正在打开文件夹，请稍后...")
            return
        # 如果没有文件夹，绘制提示信息
        if self.file_observer.root_folder is None:
            paint_alert_message(painter, self.camera, "请先打开文件夹")
        # 画场景物体

        # 画各种矩形
        if self.file_observer.root_folder:
            # self.paint_folder_dfs(painter, self.file_observer.root_folder)
            folder_style = EntityFolderDefaultStyle(
                self.file_observer.root_folder, self.file_observer.folder_max_deep_index
            )
            painter.setTransform(self.camera.get_world2view_transform())
            folder_style.paint_objects(
                PaintContext(VisualFilePainter(painter), self.camera)
            )
            painter.resetTransform()
        # 绘制选中的矩形的填充色
        for entity in self.file_observer.dragging_entity_list:
            paint_selected_rect(
                painter,
                self.camera,
                entity,
                self.file_observer.dragging_entity_activating,
            )
        # 绘制框选的矩形
        if self.file_observer.select_rect_start_location is not None:
            folder = self.file_observer.get_folder_by_location(
                self.file_observer.select_rect_start_location
            )
            user_rect = self.file_observer.select_rectangle

            if folder and user_rect:
                # 绘制框选的矩形 与 文件夹取交集
                paint_rect_in_world(
                    painter,
                    self.camera,
                    Rectangle.from_edges(
                        max(user_rect.left(), folder.body_shape.left()),
                        max(user_rect.top(), folder.body_shape.top()),
                        min(user_rect.right(), folder.body_shape.right()),
                        min(user_rect.bottom(), folder.body_shape.bottom()),
                    ),
                    QColor(255, 255, 0, 128),
                    QColor(255, 255, 0, 255),
                )
                # 绘制文件夹外框
                paint_rect_in_world(
                    painter,
                    self.camera,
                    folder.body_shape,
                    QColor(0, 0, 0, 0),
                    QColor(255, 255, 0, 255),
                )
        # 绘制细节信息
        paint_details_data(
            painter,
            self.camera,
            [
                f"{self.file_observer.root_folder.full_path if self.file_observer.root_folder else 'no root folder'}",
                f"drag locked: {self.file_observer.is_drag_locked}",
                f"drag state: {self.file_observer.interactive_state.name}",
            ],
        )

    def paint_folder_dfs(self, painter: QPainter, folder_entity: EntityFolder):
        """
        递归绘制文件夹，遇到视野之外的直接排除
        """
        # 先绘制本体
        if folder_entity.body_shape.is_collision(self.camera.cover_world_rectangle):
            paint_folder_rect(
                painter,
                self.camera,
                folder_entity,
                folder_entity.deep_level / self.file_observer.folder_max_deep_index,
            )
        else:
            return
        # 递归绘制子文件夹
        for child in folder_entity.children:
            if isinstance(child, EntityFolder):
                self.paint_folder_dfs(painter, child)
            elif isinstance(child, EntityFile):
                if child.body_shape.is_collision(self.camera.cover_world_rectangle):
                    paint_file_rect(
                        painter,
                        self.camera,
                        child,
                        child.deep_level / self.file_observer.folder_max_deep_index,
                    )

    def mousePressEvent(self, a0: QMouseEvent | None):
        assert a0 is not None
        point_view_location = NumberVector(a0.pos().x(), a0.pos().y())
        point_world_location = self.camera.location_view2world(point_view_location)

        if a0.button() == Qt.MouseButton.LeftButton:
            # 如果当前正按下的位置正好命中了正在选择的任意一个矩形，则开始拖拽
            for entity in self.file_observer.dragging_entity_list:
                if entity.body_shape.is_contain_point(point_world_location):
                    self.file_observer.interactive_state = InteractiveState.DRAG
                    break
            else:
                # 否则，开始框选
                self.file_observer.interactive_state = InteractiveState.SELECT

            # 状态更新完毕

            if self.file_observer.interactive_state == InteractiveState.SELECT:
                # 清空上一次选择的内容
                self.file_observer.dragging_entity_list = []
                # 更新选择框起始位置
                self.file_observer.select_rect_start_location = (
                    point_world_location.clone()
                )
            elif self.file_observer.interactive_state == InteractiveState.DRAG:
                # 开始拖拽，更新每个被拖拽实体的 dragging_offset
                for entity in self.file_observer.dragging_entity_list:
                    entity.dragging_offset = (
                        point_world_location - entity.body_shape.location_left_top
                    )
        elif (
            a0.button() == Qt.MouseButton.MiddleButton
            or a0.button() == Qt.MouseButton.RightButton
        ):
            # 开始准备移动，记录好上一次鼠标位置的相差距离向量
            self._last_mouse_move_location = self.camera.location_view2world(
                NumberVector(a0.pos().x(), a0.pos().y())
            )
            pass

    def _select_rect_get_entity_list(self, select_rect: Rectangle) -> list[Entity]:
        """
        选择current_folder中的实体
        选择框的起始点位置落在了什么文件夹里就直接决定它只能选中哪一个文件夹里的内容
        """
        entity_list = []

        if self.file_observer.select_rect_start_location is None:
            return entity_list

        folder = self.file_observer.get_folder_by_location(
            self.file_observer.select_rect_start_location
        )
        if folder:
            for child in folder.children:
                if child.body_shape.is_collision(select_rect):
                    entity_list.append(child)

        return entity_list

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        assert a0 is not None
        point_view_location = NumberVector(a0.pos().x(), a0.pos().y())
        point_world_location = self.camera.location_view2world(point_view_location)

        if a0.buttons() == Qt.MouseButton.LeftButton:
            if self.file_observer.interactive_state == InteractiveState.SELECT:
                # 更新矩形位置大小
                self.file_observer.select_rect_end_location = (
                    point_world_location.clone()
                )
                # 检测矩形是否和其他实体发生碰撞
                select_rect = self.file_observer.select_rectangle
                if select_rect and self.file_observer.root_folder:
                    self.file_observer.dragging_entity_list = (
                        self._select_rect_get_entity_list(select_rect)
                    )
                    pass
            elif self.file_observer.interactive_state == InteractiveState.DRAG:
                if self.file_observer.is_drag_locked:
                    return
                # 左键拖拽，但要看看是否是激活状态
                try:
                    if not self.file_observer.dragging_entity_activating:
                        # 不是一个激活的状态 就不动了
                        return
                    for entity in self.file_observer.dragging_entity_list:
                        # 让它跟随鼠标移动
                        new_left_top = point_world_location - entity.dragging_offset
                        d_location = new_left_top - entity.body_shape.location_left_top
                        entity.move(d_location)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    pass
        if (
            a0.buttons() == Qt.MouseButton.MiddleButton
            or a0.buttons() == Qt.MouseButton.RightButton
        ):
            # 移动的时候，应该记录与上一次鼠标位置的相差距离向量
            current_mouse_move_location = self.camera.location_view2world(
                NumberVector(a0.pos().x(), a0.pos().y())
            )
            diff_location = current_mouse_move_location - self._last_mouse_move_location
            self.camera.location -= diff_location

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        assert a0 is not None
        point_view_location = NumberVector(a0.pos().x(), a0.pos().y())
        point_world_location = self.camera.location_view2world(point_view_location)

        if a0.button() == Qt.MouseButton.LeftButton:
            if self.file_observer.interactive_state == InteractiveState.SELECT:
                # 左键释放，结束框选视觉效果
                self.file_observer.clear_select_rect()
                # 如果左键释放都没有找到一个实体，则在释放位置选择住一个矩形
                if not self.file_observer.dragging_entity_list:
                    point_entity = self.file_observer.get_entity_by_location(
                        point_world_location
                    )
                    # 但前提是这个矩形不能是超大矩形，即没有被屏幕完全覆盖住的
                    if point_entity and self.camera.cover_world_rectangle.is_contain(
                        point_entity.body_shape
                    ):
                        self.file_observer.dragging_entity_list = [point_entity]

            elif self.file_observer.interactive_state == InteractiveState.DRAG:
                if self.file_observer.is_drag_locked:
                    return
                self.file_observer.interactive_state = InteractiveState.SELECT

        if (
            a0.button() == Qt.MouseButton.MiddleButton
            or a0.button() == Qt.MouseButton.RightButton
        ):
            if self.file_observer.is_drag_locked:
                return

            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                pass
            else:
                # 让它脱离鼠标吸附
                self.file_observer.dragging_entity_list = []

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None):
        assert a0 is not None
        if a0.button() == Qt.MouseButton.LeftButton:
            point_view_location = NumberVector(a0.pos().x(), a0.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                open_file(entity.full_path)
        elif a0.button() == Qt.MouseButton.MiddleButton:
            # 双击中键返回原位
            self.camera.reset()

    def wheelEvent(self, a0: QWheelEvent | None):
        assert a0 is not None
        # 检查滚轮方向
        if a0.angleDelta().y() > 0:
            self.camera.zoom_in()
        else:
            self.camera.zoom_out()

        # 你可以在这里添加更多的逻辑来响应滚轮事件
        a0.accept()

    def keyPressEvent(self, a0: QKeyEvent | None):
        assert a0 is not None
        key = a0.key()
        if key == Qt.Key.Key_A:
            self.camera.press_move(NumberVector(-1, 0))
        elif key == Qt.Key.Key_S:
            self.camera.press_move(NumberVector(0, 1))
        elif key == Qt.Key.Key_D:
            self.camera.press_move(NumberVector(1, 0))
        elif key == Qt.Key.Key_W:
            self.camera.press_move(NumberVector(0, -1))

    def keyReleaseEvent(self, a0: QKeyEvent | None):
        assert a0 is not None
        key = a0.key()
        if key == Qt.Key.Key_A:
            self.camera.release_move(NumberVector(-1, 0))
        elif key == Qt.Key.Key_S:
            self.camera.release_move(NumberVector(0, 1))
        elif key == Qt.Key.Key_D:
            self.camera.release_move(NumberVector(1, 0))
        elif key == Qt.Key.Key_W:
            self.camera.release_move(NumberVector(0, -1))


def main():
    import sys
    import traceback

    try:
        sys.excepthook = sys.__excepthook__

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon("./assets/visual-file.icns"))

        canvas = Canvas()
        canvas.show()

        sys.exit(app.exec_())
    except Exception as e:
        # 捕捉不到
        traceback.print_exc()
        print(e)
        sys.exit(1)
    pass


if __name__ == "__main__":
    main()
