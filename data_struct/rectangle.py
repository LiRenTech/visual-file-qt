from data_struct.number_vector import NumberVector


class Rectangle:
    def __init__(self, location_left_top: NumberVector, width: float, height: float):
        self.location_left_top = location_left_top
        self.width = width
        self.height = height

    def __contains__(self, item) -> bool:
        if isinstance(item, NumberVector):
            return (
                    (self.location_left_top.x <= item.x <= self.location_left_top.x + self.width) and
                    (self.location_left_top.y <= item.y <= self.location_left_top.y + self.height)
            )
        else:
            return False

    def get_fore_points(self) -> list[NumberVector]:
        return [
            NumberVector(self.location_left_top.x, self.location_left_top.y),
            NumberVector(self.location_left_top.x + self.width, self.location_left_top.y),
            NumberVector(self.location_left_top.x + self.width, self.location_left_top.y + self.height),
            NumberVector(self.location_left_top.x, self.location_left_top.y + self.height)
        ]

    def is_collision(self, rect: 'Rectangle') -> bool:
        # TODO:
        return False
