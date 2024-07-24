from abc import ABC, abstractmethod

from data_struct.number_vector import NumberVector
from data_struct.rectangle import Rectangle


class Entity:
    """
    实体类
    场景里参与碰撞检测的都算实体
    """

    def __init__(self, bodyShape: Rectangle):
        self.body_shape = bodyShape

    def move(self, d_location: NumberVector):
        """
        移动实体
        :param d_location:
        :return:
        """
        self.body_shape.location_left_top += d_location

    def move_to(self, location: NumberVector):
        """
        移动实体到指定位置
        :param location:
        :return:
        """
        self.body_shape.location_left_top = location
