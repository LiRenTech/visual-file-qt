from data_struct.number_vector import NumberVector


class Rectangle:
    def __init__(self, location_left_top: NumberVector, width: float, height: float):
        self.location_left_top = location_left_top
        self.width: float = width
        self.height: float = height

    def output_data(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "locationLeftTop": [self.location_left_top.x, self.location_left_top.y],
        }

    def read_data(self, data: dict):
        self.width = data["width"]
        self.height = data["height"]
        self.location_left_top = NumberVector(
            data["locationLeftTop"][0], data["locationLeftTop"][1]
        )

    def __contains__(self, item) -> bool:
        if isinstance(item, NumberVector):
            return (
                self.location_left_top.x
                <= item.x
                <= self.location_left_top.x + self.width
            ) and (
                self.location_left_top.y
                <= item.y
                <= self.location_left_top.y + self.height
            )
        else:
            return False

    def right(self):
        """返回最右侧的x坐标

        Returns:
            float: 最右侧x坐标
        """
        return self.location_left_top.x + self.width

    def left(self):
        return self.location_left_top.x

    def top(self):
        return self.location_left_top.y

    def bottom(self):
        return self.location_left_top.y + self.height

    def get_fore_points(self) -> list[NumberVector]:
        return [
            NumberVector(self.location_left_top.x, self.location_left_top.y),
            NumberVector(
                self.location_left_top.x + self.width, self.location_left_top.y
            ),
            NumberVector(
                self.location_left_top.x + self.width,
                self.location_left_top.y + self.height,
            ),
            NumberVector(
                self.location_left_top.x, self.location_left_top.y + self.height
            ),
        ]

    @property
    def center(self) -> NumberVector:
        return NumberVector(
            self.location_left_top.x + self.width / 2,
            self.location_left_top.y + self.height / 2,
        )

    def is_collision(self, rect: "Rectangle") -> bool:
        collision_x = self.right() >= rect.left() and rect.right() >= self.left()
        collision_y = self.bottom() >= rect.top() and rect.bottom() >= self.top()
        return collision_x and collision_y


# test
if __name__ == "__main__":
    r1 = Rectangle(NumberVector(0, 0), 10, 10)
    r2 = Rectangle(NumberVector(5, 5), 10, 10)
    print(r1.is_collision(r2))  # True
    print(r2.is_collision(r1))  # True
    print(r1.center)  # (5, 5)
