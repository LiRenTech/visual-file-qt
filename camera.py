from data_struct.number_vector import NumberVector
import traceback


class Camera:
    # 每个方向上的动力矢量大小
    moveAmplitude = 2
    # 摩擦系数，越大摩擦力越大，摩擦力会使速度减慢
    frictionCoefficient = 0.1

    frictionExponent = 1.5
    """
    空气摩擦力速度指数
    指数=2，表示 f = -k * v^2
    指数=1，表示 f = -k * v
    指数越大，速度衰减越快
    """

    def __init__(self, location: NumberVector, view_width: float, view_height: float):
        self.location = location
        # 最终的渲染框大小
        self.view_width = view_width
        self.view_height = view_height

        # 大于1表示放大，小于1表示缩小
        self.current_scale = 1.0

        self.target_scale = 1.0

        self.speed = NumberVector(0, 0)
        self.accelerate = NumberVector(0, 0)
        # 可以看成一个九宫格，主要用于处理 w s a d 按键移动，
        self.accelerateCommander = NumberVector(0, 0)

    def press_move(self, moveVector: NumberVector):
        """

        :param moveVector: 四个方向的 上下左右 单位向量
        :return:
        """
        self.accelerateCommander += moveVector
        self.accelerateCommander = self.accelerateCommander.limit_x(-1, 1)
        self.accelerateCommander = self.accelerateCommander.limit_y(-1, 1)

    def release_move(self, moveVector: NumberVector):
        self.accelerateCommander -= moveVector
        self.accelerateCommander = self.accelerateCommander.limit_x(-1, 1)
        self.accelerateCommander = self.accelerateCommander.limit_y(-1, 1)

    def zoom_in(self):
        self.target_scale *= 1.1

    def zoom_out(self):
        self.target_scale /= 1.1

    def tick(self):
        try:
            # 计算摩擦力
            friction = NumberVector.zero()
            if not self.speed.is_zero():
                speed_size = self.speed.magnitude()
                friction = self.speed.normalize() * -1 * (
                        self.frictionCoefficient * speed_size ** self.frictionExponent)
            self.speed += self.accelerateCommander * (self.moveAmplitude * (1 / self.current_scale))
            self.speed += friction

            self.location += self.speed

            # 让 current_scale 逐渐靠近 target_scale
            self.current_scale += (self.target_scale - self.current_scale) / 10
        except Exception as e:
            traceback.print_exc()
            print(e)

    def location_world2view(self, world_location: NumberVector) -> NumberVector:
        """
        将世界坐标转换成视野渲染坐标
        :param world_location:
        :return:
        """
        diff: NumberVector = NumberVector(self.view_width / 2, self.view_height / 2)
        v: NumberVector = (world_location - self.location) * self.current_scale
        return v + diff

    def location_view2world(self, view_location: NumberVector) -> NumberVector:
        """
        将视野渲染坐标转换成世界坐标
        :param view_location:
        :return:
        """
        v: NumberVector = (view_location - NumberVector(self.view_width / 2,
                                                        self.view_height / 2)) / self.current_scale
        return v + self.location
