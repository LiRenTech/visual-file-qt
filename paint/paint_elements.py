from PyQt5.QtGui import QPainter, QColor

from camera import Camera
from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle
from entity.entity import Entity
from entity.entity_file import EntityFile
from entity.entity_folder import EntityFolder
from paint.paint_utils import PainterUtils
from tools.color_utils import get_color_by_level


def paint_grid(paint: QPainter, camera: Camera):
    try:
        line_color = QColor(255, 255, 255, 100)
        line_color_light = QColor(255, 255, 255, 255)

        for y in range(-1000, 1000, 100):
            PainterUtils.paint_solid_line(
                paint,
                camera.location_world2view(NumberVector(-1000, y)),
                camera.location_world2view(NumberVector(1000, y)),
                line_color_light if y == 0 else line_color,
                1 * camera.current_scale,
            )
        for x in range(-1000, 1000, 100):
            PainterUtils.paint_solid_line(
                paint,
                camera.location_world2view(NumberVector(x, -1000)),
                camera.location_world2view(NumberVector(x, 1000)),
                line_color_light if x == 0 else line_color,
                1 * camera.current_scale,
            )
    except Exception as e:
        print(e)


def paint_details_data(paint: QPainter, camera: Camera, datas: list[str]):
    """
    左上角绘制细节信息
    :param paint:
    :param camera:
    :param datas:
    :return:
    """
    start_y = 100
    PainterUtils.paint_word_from_left_top(
        paint,
        NumberVector(0, 50),  # 左上角坐标
        f"camera scale: {camera.current_scale:.2f} location: {camera.location}",
        12,
        QColor(255, 255, 255, 100),
    )
    for i, data in enumerate(datas):
        PainterUtils.paint_word_from_left_top(
            paint,
            NumberVector(0, start_y + i * 50),
            data,
            12,
            QColor(255, 255, 255, 100),
        )
    pass


def paint_alert_message(paint: QPainter, camera: Camera, message: str):
    """
    屏幕中心绘制警告信息
    :param paint:
    :param camera:
    :param message:
    :return:
    """

    PainterUtils.paint_word_from_center(
        paint,
        NumberVector(camera.view_width / 2, camera.view_height / 2),
        message,
        24,
        QColor(255, 255, 0, 255),
    )


def paint_rect_in_world(
    paint: QPainter,
    camera: Camera,
    rect: Rectangle,
    fill_color: QColor,
    stroke_color: QColor,
):
    PainterUtils.paint_rect_from_left_top(
        paint,
        camera.location_world2view(rect.location_left_top),
        rect.width * camera.current_scale,
        rect.height * camera.current_scale,
        fill_color,
        stroke_color,
        1,
    )


def paint_file_rect(
    paint: QPainter, camera: Camera, entity_file: EntityFile, color_rate: float = 0.5
):

    # 先画一个框
    PainterUtils.paint_rect_from_left_top(
        paint,
        camera.location_world2view(entity_file.body_shape.location_left_top),
        entity_file.body_shape.width * camera.current_scale,
        entity_file.body_shape.height * camera.current_scale,
        QColor(0, 0, 0, 255),
        get_color_by_level(color_rate),
        1,
    )
    # camera scale < 0.15 的时候不渲染文字了，会导致文字突然变大，重叠一大堆
    if camera.current_scale < 0.15:
        return
    # 再画文字
    PainterUtils.paint_word_from_left_top(
        paint,
        camera.location_world2view(
            entity_file.body_shape.location_left_top + NumberVector(5, 5)
        ),
        entity_file.file_name,
        14 * camera.current_scale,
        get_color_by_level(color_rate),
    )

    pass


def paint_selected_rect(
    paint: QPainter, camera: Camera, selected_entity: Entity, is_active: bool
):
    """
    绘制选中的区域
    :param paint:
    :param camera:
    :param selected_entity:
    :param is_active: 如果是激活状态，绘制填充颜色，否则绘制边框颜色
    :return:
    """
    PainterUtils.paint_rect_from_left_top(
        paint,
        camera.location_world2view(
            selected_entity.body_shape.location_left_top - NumberVector(5, 5)
        ),
        (selected_entity.body_shape.width + 10) * camera.current_scale,
        (selected_entity.body_shape.height + 10) * camera.current_scale,
        QColor(89, 158, 94, 100) if is_active else QColor(0, 0, 0, 0),
        QColor(0, 255, 0, 255) if is_active else QColor(255, 0, 0, 255),
        4,
    )


def paint_folder_rect(
    paint: QPainter, camera: Camera, entity_file: EntityFolder, color_rate: float = 0.5
):
    """

    :param paint:
    :param camera:
    :param entity_file:
    :param color_rate:
    :return:
    """
    # 先画一个框
    PainterUtils.paint_rect_from_left_top(
        paint,
        camera.location_world2view(entity_file.body_shape.location_left_top),
        entity_file.body_shape.width * camera.current_scale,
        entity_file.body_shape.height * camera.current_scale,
        QColor(255, 255, 255, 0),
        get_color_by_level(color_rate),
        1,
    )
    if camera.current_scale < 0.05:
        return
    # 再画文字
    PainterUtils.paint_word_from_left_top(
        paint,
        camera.location_world2view(entity_file.body_shape.location_left_top),
        entity_file.folder_name,
        16 * camera.current_scale,
        get_color_by_level(color_rate),
    )
