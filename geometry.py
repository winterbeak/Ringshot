import math


def angle_between(from_position, to_position):
    delta_x = to_position[0] - from_position[0]
    delta_y = to_position[1] - from_position[1]
    return math.atan2(delta_y, delta_x)


def simple_vector(angle, magnitude):
    delta_x = math.cos(angle) * magnitude
    delta_y = math.sin(angle) * magnitude
    return delta_x, delta_y
