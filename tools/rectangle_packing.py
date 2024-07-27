from typing import List
from data_struct.rectangle import Rectangle
from data_struct.number_vector import NumberVector


"""
装箱问题，排序矩形
    :param rectangles: N个矩形的大小和位置
    :param margin: 矩形之间的间隔（为了美观考虑）
    :return: 调整好后的N个矩形的大小和位置，数组内每个矩形一一对应。
    例如：
    rectangles = [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(10, 10), 1, 1)]
    这两个矩形对角放，外套矩形空隙面积过大，空间浪费，需要调整位置。

    调整后返回：

    [Rectangle(NumberVector(0, 0), 10, 10), Rectangle(NumberVector(12, 0), 1, 1)]
    参数 margin = 2
    横向放置，减少了空间浪费。
"""


def sort_rectangle_just_vertical(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """
    仅仅将一些矩形左对齐 竖向简单排列
    这会假设外层父文件夹左上角顶点为 0 0
    :param rectangles:
    :param margin:
    :return:
    """
    current_y = margin

    for rectangle in rectangles:
        rectangle.location_left_top.y = current_y
        rectangle.location_left_top.x = margin
        current_y += rectangle.height + margin

    return rectangles

def sort_rectangle_greedy(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """贪心策略"""
    if len(rectangles) == 0:
        return []

    def append_right(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> Rectangle:
        ret = Rectangle(
            NumberVector(rect.location_left_top.x, rect.location_left_top.y),
            rect.width,
            rect.height,
        )
        ret.location_left_top.x = origin.right() + margin
        ret.location_left_top.y = origin.top()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if ret.is_collision(r):
                    ret.location_left_top.y = r.bottom() + margin
                    collision = True
                    break
        return ret

    def append_bottom(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> Rectangle:
        ret = Rectangle(
            NumberVector(rect.location_left_top.x, rect.location_left_top.y),
            rect.width,
            rect.height,
        )
        ret.location_left_top.y = origin.bottom() + margin
        ret.location_left_top.x = origin.left()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if ret.is_collision(r):
                    ret.location_left_top.x = r.right() + margin
                    collision = True
                    break
        return ret

    rectangles[0].location_left_top.x = 0
    rectangles[0].location_left_top.y = 0
    ret = [rectangles[0]]
    width = rectangles[0].width
    height = rectangles[0].height
    # index = 0
    for i in range(1, len(rectangles)):
        # if width < height:
        #     rectangles[i] = append_right(rectangles[index], rectangles[i], ret)
        #     w = rectangles[i].right()
        #     if w > width:
        #         width = w
        #         index = i
        # else:
        #     rectangles[i] = append_bottom(rectangles[index], rectangles[i], ret)
        #     h = rectangles[i].bottom()
        #     if h > height:
        #         height = h
        #         index = i
        # ret.append(rectangles[i])
        min_space_score = -1
        min_shape_score = -1
        min_rect = None
        for j in range(len(ret)):
            r = append_right(ret[j], rectangles[i], ret)
            space_score = r.right() - width + r.bottom() - height
            shape_score = abs(max(r.right(), width) - max(r.bottom(), height))
            if (
                min_space_score == -1
                or space_score < min_space_score
                or (space_score == min_space_score and shape_score < min_shape_score)
            ):
                min_space_score = space_score
                min_shape_score = shape_score
                min_rect = r
            r = append_bottom(ret[j], rectangles[i], ret)
            space_score = r.right() - width + r.bottom() - height
            shape_score = abs(max(r.right(), width) - max(r.bottom(), height))
            if (
                min_space_score == -1
                or space_score < min_space_score
                or (space_score == min_space_score and shape_score < min_shape_score)
            ):
                min_space_score = space_score
                min_shape_score = shape_score
                min_rect = r
        width = max(width, r.right())
        height = max(height, r.bottom())
        assert min_rect is not None
        ret.append(min_rect)

    return ret


def sort_rectangle_right_bottom(
    rectangles: list[Rectangle], margin: float
) -> list[Rectangle]:
    """不停的往右下角放的策略"""

    def append_right(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> None:
        rect.location_left_top.x = origin.right() + margin
        rect.location_left_top.y = origin.top()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if rect.is_collision(r):
                    rect.location_left_top.y = r.bottom() + margin
                    collision = True
                    break

    def append_bottom(
        origin: Rectangle, rect: Rectangle, rects: list[Rectangle]
    ) -> None:
        rect.location_left_top.y = origin.bottom() + margin
        rect.location_left_top.x = origin.left()
        # 碰撞检测
        collision = True
        while collision:
            collision = False
            for r in rects:
                if rect.is_collision(r):
                    rect.location_left_top.x = r.right() + margin
                    collision = True
                    break

    rectangles[0].location_left_top.x = 0
    rectangles[0].location_left_top.y = 0
    ret = [rectangles[0]]
    width = rectangles[0].width
    height = rectangles[0].height
    index = 0
    for i in range(1, len(rectangles)):
        if width < height:
            append_right(rectangles[index], rectangles[i], ret)
            w = rectangles[i].right()
            if w > width:
                width = w
                index = i
        else:
            append_bottom(rectangles[index], rectangles[i], ret)
            h = rectangles[i].bottom()
            if h > height:
                height = h
                index = i
        ret.append(rectangles[i])

    return ret
