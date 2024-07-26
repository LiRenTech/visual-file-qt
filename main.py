import traceback
import json

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDesktopWidget,
    QAction,
    QMainWindow,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent, QKeyEvent, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, QPoint

from assets import assets

# 是为了引入assets文件夹中的资源文件，看似是灰色的没有用，但实际不能删掉
# 只是为了让pyinstaller打包时能打包到exe文件中。
# 需要进入assets文件夹后在命令行输入指令 `pyrcc5 image.rcc -o assets.py` 来更新assets.py文件

from camera import Camera
from data_struct.number_vector import NumberVector
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from file_observer import FileObserver
from file_openner import open_file
from paint.paint_elements import (
    paint_grid,
    paint_file_rect,
    paint_rect_in_world,
    paint_folder_rect,
    paint_details_data,
    paint_selected_rect,
    paint_alert_message,
)
from paint.paint_utils import PainterUtils

# READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire/test_file"
READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire"
READ_FOLDER = r"D:\Projects\Project-CannonWar\CannonWar-v2\src"


# READ_FOLDER = "D:/Desktop/test"


class Canvas(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # 重要对象绑定
        self.camera = Camera(NumberVector.zero(), 1920, 1080)
        self.file_observer = FileObserver(READ_FOLDER)

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

    def init_ui(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle("VisualFile 大型文件夹直观可视化工具")

        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon(":/favicon.ico"))
        self._move_window_to_center()

        # 创建菜单栏
        menubar = self.menuBar()
        # 创建 "File" 菜单
        file_menu = menubar.addMenu("File")
        # 创建 "Open" 菜单项
        open_action = QAction("直接读取文件夹", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        open_action.triggered.connect(self.on_open)

        # 创建 "Save" 菜单项
        save_action = QAction("导出布局文件", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        save_action.triggered.connect(self.on_save)

        # 创建 "Update" 菜单项
        update_action = QAction("更新文件夹", self)
        update_action.setShortcut("Ctrl+U")
        file_menu.addAction(update_action)
        update_action.triggered.connect(self.on_update)

        # 创建 导入 菜单项
        import_action = QAction("导入布局文件并更新布局", self)
        import_action.setShortcut("Ctrl+I")
        file_menu.addAction(import_action)
        import_action.triggered.connect(self.on_import)

        # "View" 菜单
        view_menu = menubar.addMenu("View")
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

        drag_lock = QAction("锁定拖拽", self)
        drag_lock.setShortcut("Ctrl+L")
        view_menu.addAction(drag_lock)
        drag_lock.triggered.connect(lambda: self.file_observer.set_drag_lock(True))

        drag_unlock = QAction("解锁拖拽", self)
        drag_unlock.setShortcut("Ctrl+U")
        view_menu.addAction(drag_unlock)
        drag_unlock.triggered.connect(lambda: self.file_observer.set_drag_lock(False))

        # 创建帮助说明菜单项
        help_menu = menubar.addMenu("Help")
        help_action = QAction("帮助说明", self)
        help_action.setShortcut("Ctrl+H")
        help_menu.addAction(help_action)
        help_action.triggered.connect(self.on_help)

        pass

    def _move_window_to_center(self):
        # 获取屏幕的尺寸和中心位置
        screen = QDesktopWidget().screenGeometry()
        screen_center = screen.center()

        # 计算窗口的中心位置
        window_size = self.geometry().size()
        window_center = QPoint(window_size.width() // 2, window_size.height() // 2)

        # 计算窗口的左上角位置以使其居中
        window_top_left = screen_center - window_center
        self.move(window_top_left)

    def on_help(self):
        # 创建一个消息框
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon(":/favicon.ico"))
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("visual-file 帮助说明")
        msgBox.setText(
            "点击某矩形拖拽\n双击矩形：打开对应文件\n鼠标中键或者WSAD：移动视野\n鼠标滚轮：缩放视野\n"
        )
        msgBox.setStandardButtons(QMessageBox.Ok)

        # 显示消息框
        msgBox.exec_()

    def on_open(self):
        # 直接读取文件
        directory = QFileDialog.getExistingDirectory(self, "选择要直观化查看的文件夹")

        if directory:
            self.file_observer.update_file_path(directory)
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
        # 更新文件夹内容
        print("更新文件")
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

            print(type(layout_dict), layout_dict)
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
        if self.file_observer.dragging_entity:
            # 对比当前选中的实体矩形和视野矩形
            if self.camera.cover_world_rectangle.is_contain(
                self.file_observer.dragging_entity.body_shape
            ):
                # 套住了
                self.file_observer.dragging_entity_activating = True
                pass
            else:
                # 没套住
                self.file_observer.dragging_entity_activating = False
                pass
            pass
        # 重绘窗口
        self.update()

    def paintEvent(self, event):
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
            # 正在更新布局，绘制一个提醒
            paint_alert_message(painter, self.camera, "正在更新文件夹内容，请稍后...")
            return
        # 画场景物体

        # 先画文件夹
        is_danger = False
        for folder_entity in self.file_observer.get_entity_folders():
            if not folder_entity.body_shape:
                print(folder_entity)
                print(f"warn!,[folder] {folder_entity.full_path} body shape is None")
                is_danger = True
                continue
            if folder_entity.body_shape.is_collision(
                self.camera.cover_world_rectangle
            ):  # bodyShape可能是None
                # 获得一个世界坐标系的视野矩形，用于排除视野之外的绘制，防止放大了之后会卡
                paint_folder_rect(painter, self.camera, folder_entity)
        # 后画文件
        for file_entity in self.file_observer.get_entity_files():
            if not file_entity.body_shape:
                print(f"warn!,[file] {file_entity.full_path} body shape is None")
                is_danger = True
                continue
            if file_entity.body_shape.is_collision(self.camera.cover_world_rectangle):
                paint_file_rect(painter, self.camera, file_entity)
        if is_danger:
            exit(1)
        # 绘制选中的区域
        paint_selected_rect(
            painter,
            self.camera,
            self.file_observer.dragging_entity,
            self.file_observer.dragging_entity_activating,
        )
        # 绘制细节信息
        paint_details_data(
            painter,
            self.camera,
            [
                f"{self.file_observer.root_folder.full_path}",
                f"drag locked: {self.file_observer.is_drag_locked}",
            ],
        )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:

                # 让它吸附在鼠标上
                if isinstance(entity, EntityFile):
                    pass
                elif isinstance(entity, EntityFolder):
                    pass
                self.file_observer.dragging_entity = entity
                self.file_observer.dragging_offset = (
                    point_world_location - entity.body_shape.location_left_top
                )
            else:
                self.file_observer.dragging_entity = None
        elif event.button() == Qt.MiddleButton:
            # 开始准备移动，记录好上一次鼠标位置的相差距离向量
            self._last_mouse_move_location = self.camera.location_view2world(
                NumberVector(event.pos().x(), event.pos().y())
            )
            pass

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            if self.file_observer.is_drag_locked:
                return
            # 左键拖拽，但要看看是否是激活状态
            try:
                point_view_location = NumberVector(event.pos().x(), event.pos().y())
                point_world_location = self.camera.location_view2world(
                    point_view_location
                )
                if self.file_observer.dragging_entity:
                    if not self.file_observer.dragging_entity_activating:
                        # 不是一个激活的状态 就不动了
                        return
                    # 让它跟随鼠标移动
                    new_left_top = (
                        point_world_location - self.file_observer.dragging_offset
                    )
                    d_location = (
                        new_left_top
                        - self.file_observer.dragging_entity.body_shape.location_left_top
                    )
                    self.file_observer.dragging_entity.move(d_location)
            except Exception as e:
                print(e)
                traceback.print_exc()
                pass
        if event.buttons() == Qt.MiddleButton:
            # 移动的时候，应该记录与上一次鼠标位置的相差距离向量
            current_mouse_move_location = self.camera.location_view2world(
                NumberVector(event.pos().x(), event.pos().y())
            )
            diff_location = current_mouse_move_location - self._last_mouse_move_location
            self.camera.location -= diff_location

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.file_observer.is_drag_locked:
                return
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                pass
            else:
                # 让它脱离鼠标吸附
                self.file_observer.dragging_entity = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                open_file(entity.full_path)

        pass

    def wheelEvent(self, event: QWheelEvent):
        # 检查滚轮方向
        if event.angleDelta().y() > 0:
            self.camera.zoom_in()
        else:
            self.camera.zoom_out()

        # 你可以在这里添加更多的逻辑来响应滚轮事件
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_A:
            self.camera.press_move(NumberVector(-1, 0))
        elif key == Qt.Key_S:
            self.camera.press_move(NumberVector(0, 1))
        elif key == Qt.Key_D:
            self.camera.press_move(NumberVector(1, 0))
        elif key == Qt.Key_W:
            self.camera.press_move(NumberVector(0, -1))

    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key_A:
            self.camera.release_move(NumberVector(-1, 0))
        elif key == Qt.Key_S:
            self.camera.release_move(NumberVector(0, 1))
        elif key == Qt.Key_D:
            self.camera.release_move(NumberVector(1, 0))
        elif key == Qt.Key_W:
            self.camera.release_move(NumberVector(0, -1))


def main():
    import sys
    import traceback

    try:
        sys.excepthook = sys.__excepthook__

        app = QApplication(sys.argv)

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
