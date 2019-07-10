import math


def magnitude(components):
    """Returns the magnitude of a vector given the x and y components."""
    return math.sqrt(components[0] ** 2 + components[1] ** 2)


def angle_between(from_position, to_position):
    delta_x = to_position[0] - from_position[0]
    delta_y = to_position[1] - from_position[1]
    return math.atan2(delta_y, delta_x)


def vector_to_difference(angle, magnitude):
    """Converts a vector into a difference of x and a difference of y."""
    delta_x = math.cos(angle) * magnitude
    delta_y = math.sin(angle) * magnitude
    return delta_x, delta_y


def difference_to_vector(difference):
    """Converts a (delta_x, delta_y) pair into an (angle, magnitude) pair.

    Note that the y axis is inverted, since that's what pygame does."""
    delta_x, delta_y = difference
    magnitude = math.sqrt(delta_x ** 2 + delta_y ** 2)

    if delta_x == 0.0:
        angle = math.atan(math.inf)
        if delta_y < 0.0:
            angle += math.pi
    else:
        # quadrants are weird here because moving down is positive!
        angle = math.atan(abs(delta_y / delta_x))

        if delta_x < 0.0:
            if delta_y < 0.0:  # quadrant 2
                angle = math.pi - angle
            else:              # quadrant 3
                angle += math.pi
        else:
            if delta_y > 0.0:  # quadrant 4
                angle = math.pi * 2.0 - angle

    # print("%.2f / %.2f" % (delta_y, delta_x))

    return angle, magnitude


def component_in_direction(vector, direction):
    """Returns the magnitude of the component of a vector that points in
    the given direction.
    NOTE: sometimes is negative, which I take advantage of when
    calculating angular velocity

    vector is an (angle, magnitude) pair.
    """
    angle, magnitude = vector
    delta_angle = abs(direction - angle)
    return magnitude * math.cos(delta_angle)


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def two_point_slope(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if x1 == x2:
        return math.inf
    return float(y2 - y1) / float(x2 - x1)


def y_intercept(point, slope):
    if math.isinf(slope):
        return None
    x, y = point
    return y - slope * x


def segment_extended_intersection(segment1, segment2):
    """Returns the intersection of two segments, as if the segments were
    extended infinitely.

    Note that if there are infinite intersection points, or if there are
    no intersection points, the function will return None.
    """
    if math.isclose(segment1.slope, segment2.slope):
        return None

    m1 = segment1.slope
    m2 = segment2.slope
    b1 = segment1.y_intercept
    b2 = segment2.y_intercept

    if math.isinf(segment1.slope):
        x = segment1.x_intercept
        y = m2 * x + b2

    elif math.isinf(segment2.slope):
        x = segment2.x_intercept
        y = m1 * x + b1

    else:
        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1
    return x, y


def inverse(num):
    """Returns the inverse of a number.

    Interestingly, Python automatically handles 1.0 / inf.
    """
    if num == 0.0:
        return math.inf
    return 1.0 / num


def min_and_max(num1, num2):
    """Returns a tuple, which is the (minimum, maximum) of the two numbers."""
    if num1 < num2:
        return num1, num2
    else:
        return num2, num1


def on_segment(point, segment, know_on_line=False):
    """Checks if a point is on a given segment.

    If the point is already known to be on the line of the segment (i.e. the
    point is on the line you get from stretching the segment infinitely), then
    you can skip some calculations by setting know_on_line to True.
    """
    if math.isinf(segment.slope):
        if know_on_line or math.isclose(segment.x_intercept, point[0]):
            min_y, max_y = min_and_max(segment.point1[1], segment.point2[1])

            if min_y < point[1] < max_y:
                return True

        return False

    if not know_on_line:
        check_y = segment.slope * point[0] + segment.y_intercept

        if not math.isclose(point[1], check_y):
            return False

    min_x, max_x = min_and_max(segment.point1[0], segment.point2[0])

    if min_x < point[0] < max_x:
        return True
    return False


class Segment:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

        self.length = distance(point1, point2)
        self.slope = two_point_slope(point1, point2)

        # y_intercept is stored as if the segment was infinite
        self.y_intercept = y_intercept(point1, self.slope)
        if self.slope == 0.0:
            self.x_intercept = None
        elif math.isinf(self.slope):
            self.x_intercept = point1[0]
        else:
            self.x_intercept = -self.y_intercept / self.slope

    def print(self):
        print(self.point1, self.point2)


def points_to_segment_list(point_list):
    """Returns a list of segments from point 1 to point 2, point 2 to point 3
    all the way to point N to point 1.  All points are (x, y) pairs.

    Sending one or less points returns an empty list.  Sending two points
    returns a single segment between point 1 and point 2.
    """
    last_point = len(point_list) - 1
    if last_point <= 0:
        return []
    if last_point == 1:
        return [Segment(point_list[0], point_list[1])]

    segment_list = []
    for i in range(last_point):
        segment_list.append(Segment(point_list[i], point_list[i + 1]))
    segment_list.append(Segment(point_list[last_point], point_list[0]))

    return segment_list


def point_and_segment(point, segment):
    """Previously known as shortest_segment_between_point_and_segment().
    Returns the shortest line segment that would connect a given point and
    a given Segment.

    Returns None if the point is already on the segment.
    """
    if on_segment(point, segment):
        return None

    check_slope = -inverse(segment.slope)
    if math.isinf(check_slope):
        # generates a segment that is arbitrarily 10 unit long
        check_segment = Segment(point, (point[0], point[1] + 10))
    else:
        check_y_intercept = y_intercept(point, check_slope)
        check_segment = Segment(point, (0.0, check_y_intercept))

    intersection = segment_extended_intersection(check_segment, segment)
    if not intersection:
        return None

    if on_segment(intersection, segment, True):
        return Segment(intersection, point)

    else:
        distance1 = distance(point, segment.point1)
        distance2 = distance(point, segment.point2)
        if distance1 < distance2:
            return Segment(point, segment.point1)
        else:
            return Segment(point, segment.point2)


def reflect_vector(slope, delta):
    angle1, magnitude = difference_to_vector(delta)

    angle2 = math.atan(slope)
    delta_angle = angle2 - angle1
    final_angle = angle2 + delta_angle

    # print(math.degrees(angle1))
    # print(math.degrees(angle2))
    # print(math.degrees(final_angle))

    return vector_to_difference(final_angle, magnitude)


# test_segment = Segment((0.0, 0.0), (100.0, 100.0))
# test_point = (1.0, 3.0)
# result_segment = point_and_segment(test_point, test_segment)
# result_segment.print()
#
# print(reflect_vector(1.0, (-5.0, -5.0)))
