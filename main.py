import traceback

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent, QKeyEvent, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer

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
)

# READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire/test_file"
READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire"
READ_FOLDER = r"D:\Projects\Project-CannonWar\CannonWar-v2\src"


# READ_FOLDER = "D:/Desktop/test"


class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle("VisualFile 大型文件夹直观可视化工具")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon(":/favicon.ico"))
        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.camera = Camera(NumberVector.zero(), 1920, 1080)

        # 文件和内容相关
        self.file_observer = FileObserver(READ_FOLDER)

        # 创建一个定时器用于定期更新窗口
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(16)  # 1000/60 大约= 16ms
        # 启动定时器
        self.timer.start()

        # 窗口移动相关
        self._last_mouse_move_location = NumberVector.zero()  # 注意这是一个世界坐标

    def tick(self):
        self.camera.tick()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 获取窗口的尺寸
        rect = self.rect()
        # 更新camera大小，防止放大窗口后缩放中心点还在左上部分
        self.camera.reset_view_size(rect.width(), rect.height())
        # 获得一个世界坐标系的视野矩形，用于排除视野之外的绘制，防止放大了之后会卡
        from data_struct.rectangle import Rectangle

        world_rect = Rectangle(
            self.camera.location_view2world(NumberVector(0, 0)),
            rect.width() / self.camera.current_scale,
            rect.height() / self.camera.current_scale,
        )

        # 使用黑色填充整个窗口
        painter.fillRect(rect, Qt.black)
        # 画网格
        paint_grid(painter, self.camera)

        # 画场景物体
        # 绘制选中的浅色底层
        paint_selected_rect(painter, self.camera, self.file_observer.dragging_entity)
        # 先画文件夹
        for folder_entity in self.file_observer.get_entity_folders():
            if folder_entity.body_shape.is_collision(world_rect):
                paint_folder_rect(painter, self.camera, folder_entity)
        # 后画文件
        for file_entity in self.file_observer.get_entity_files():
            if file_entity.body_shape.is_collision(world_rect):
                paint_file_rect(painter, self.camera, file_entity)

        # 画选中的框
        if self.file_observer.dragging_entity:
            paint_rect_in_world(
                painter,
                self.camera,
                self.file_observer.dragging_entity.body_shape,
                QColor(0, 0, 0, 0),
                QColor(255, 0, 0),
            )
        # 绘制细节信息
        paint_details_data(painter, self.camera)

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
            try:
                point_view_location = NumberVector(event.pos().x(), event.pos().y())
                point_world_location = self.camera.location_view2world(
                    point_view_location
                )
                if self.file_observer.dragging_entity:
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
