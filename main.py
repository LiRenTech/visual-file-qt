from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QMouseEvent, QWheelEvent, QKeyEvent, QColor
from PyQt5.QtCore import Qt, QPoint, QTimer

from camera import Camera
from data_struct.number_vector import NumberVector
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from file_observer import FileObserver
from file_openner import open_file
from paint.paint_elements import paint_grid, paint_file_rect, paint_rect_in_world, paint_folder_rect
from paint.paint_utils import PainterUtils

# READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire/test_file"
READ_FOLDER = "D:/Projects/Project-Tools/CodeEmpire"


class Canvas(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle('Code Empire 代码帝国')
        self.setGeometry(0, 0, 1920, 1080)
        # 设置窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.camera = Camera(NumberVector.zero(), 1920, 1080)

        # 文件和内容相关
        self.file_path = ""
        self.file_observer = FileObserver(READ_FOLDER)

        # 创建一个定时器用于定期更新窗口
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(16)  # 1000/60 大约= 16ms
        # 启动定时器
        self.timer.start()

    def tick(self):
        self.camera.tick()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 获取窗口的尺寸
        rect = self.rect()
        # 使用黑色填充整个窗口
        painter.fillRect(rect, Qt.black)
        # 画网格
        paint_grid(painter, self.camera)

        # 画场景物体
        # 先画文件夹
        for folder_entity in self.file_observer.get_entity_folders():
            paint_folder_rect(painter, self.camera, folder_entity)
        # 后画文件
        for file_entity in self.file_observer.get_entity_files():
            paint_file_rect(painter, self.camera, file_entity)

        # 画选中的框
        if self.file_observer.dragging_entity:
            paint_rect_in_world(
                painter,
                self.camera,
                self.file_observer.dragging_entity.body_shape,
                QColor(0, 0, 0, 0),
                QColor(255, 0, 0)
            )

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                # 让它吸附在鼠标上
                if isinstance(entity, EntityFile):
                    print(entity.full_path)
                    pass
                elif isinstance(entity, EntityFolder):
                    print(entity.full_path)
                    pass
                self.file_observer.dragging_entity = entity
                self.file_observer.dragging_offset = point_world_location - entity.body_shape.location_left_top
            else:
                self.file_observer.dragging_entity = None
            pass

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            if self.file_observer.dragging_entity:
                # 让它跟随鼠标移动
                print(self.file_observer.dragging_entity)
                new_left_top = point_world_location - self.file_observer.dragging_offset
                d_location = new_left_top - self.file_observer.dragging_entity.body_shape.location_left_top
                self.file_observer.dragging_entity.move(d_location)

                self.file_observer.dragging_entity.parent.adjust()
                pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            point_view_location = NumberVector(event.pos().x(), event.pos().y())
            point_world_location = self.camera.location_view2world(point_view_location)
            entity = self.file_observer.get_entity_by_location(point_world_location)
            if entity:
                print("release", entity)
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


if __name__ == '__main__':
    main()
