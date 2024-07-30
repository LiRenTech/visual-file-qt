class NumberVector:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, location_left_top: NumberVector, width: float, height: float):
        self.location_left_top = location_left_top
        self.width = width
        self.height = height


def sort_rectangle(rectangles: list[Rectangle], margin: float) -> list[Rectangle]:
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
    return rectangles


def show_rectangle(rectangles: list[Rectangle]):
    """
    用海龟绘图 显示所有矩形
    """
    import turtle

    # 创建一个绘图窗口
    screen = turtle.Screen()
    screen.title("Rectangle Visualization")

    # 创建一个小海龟绘图器
    painter = turtle.Turtle()
    painter.speed(0)  # 设置绘制速度为最快

    # 遍历所有矩形进行绘制
    for rect in rectangles:
        # 移动到矩形的左上角位置
        painter.penup()  # 抬起笔，移动时不绘制
        painter.goto(rect.location_left_top.x, -rect.location_left_top.y)
        painter.pendown()  # 放下笔，开始绘制

        # 绘制矩形
        for _ in range(2):
            painter.forward(rect.width)  # 向右移动
            painter.left(90)  # 左转90度
            painter.forward(rect.height)  # 向下移动
            painter.left(90)  # 左转90度

    # 隐藏海龟
    painter.hideturtle()

    # 结束绘制
    screen.mainloop()


def main():
    rectangles_list = [
        # 斜对角放置两个
        sort_rectangle(
            [
                Rectangle(NumberVector(0, 0), 10, 10),
                Rectangle(NumberVector(10, 10), 1, 1),
            ],
            2,
        ),
        # 五个长条文件
        sort_rectangle(
            [
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 500, 100),
            ],
            50,
        ),
        # 五个参差不齐的长条
        sort_rectangle(
            [
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 600, 100),
                Rectangle(NumberVector(0, 0), 750, 100),
                Rectangle(NumberVector(0, 0), 400, 100),
                Rectangle(NumberVector(0, 0), 200, 100),
            ],
            50,
        ),
        # 五个正方形
        sort_rectangle(
            [
                Rectangle(NumberVector(0, 0), 100, 100),
                Rectangle(NumberVector(0, 0), 100, 100),
                Rectangle(NumberVector(0, 0), 100, 100),
                Rectangle(NumberVector(0, 0), 100, 100),
                Rectangle(NumberVector(0, 0), 100, 100),
            ],
            50,
        ),
        # 四个长条文件和一个大正方形文件夹
        sort_rectangle(
            [
                Rectangle(NumberVector(0, 0), 500, 100),
                Rectangle(NumberVector(0, 0), 520, 100),
                Rectangle(NumberVector(0, 0), 540, 100),
                Rectangle(NumberVector(0, 0), 456, 100),
                Rectangle(NumberVector(0, 0), 600, 1000),
            ],
            50,
        ),
    ]

    show_rectangle(rectangles_list[2])


if __name__ == "__main__":
    main()
