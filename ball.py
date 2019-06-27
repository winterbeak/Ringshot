import pygame
import constants
import geometry


class Ball:
    """A simulated ball that experiences gravity and rolls."""
    DEBUG_COLOR = constants.MAGENTA

    def __init__(self, position, radius):
        self.x = position[0]
        self.y = position[1]
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.x_acceleration = 0.0
        self.y_acceleration = 0.0
        self.position = position
        self.radius = radius

    def draw_debug(self, surface):
        position = (int(self.x), int(self.y))  # pygame circles use integers
        pygame.draw.circle(surface, self.DEBUG_COLOR, position, self.radius)

    def move(self, distance):
        """Instantly moves the ball a certain distance from its
        current position."""
        self.x = self.x + distance[0]
        self.y = self.y + distance[1]
        self.position = (self.x, self.y)

    def goto(self, position):
        """Instantly moves the ball to a certain position on the screen."""
        self.x = position[0]
        self.y = position[1]
        self.position = position

    def update_position(self, slowmo_factor=1.0):
        """Moves the ball according to its velocity and acceleration.

        slowmo_factor is how much the ball slows down due to slowmo."""
        self.y_acceleration = constants.GRAVITY

        distance_x = self.x_velocity / slowmo_factor
        distance_y = self.y_velocity / slowmo_factor
        self.move((distance_x, distance_y))

        self.x_velocity += self.x_acceleration / slowmo_factor
        self.y_velocity += self.y_acceleration / slowmo_factor

    def launch(self, direction, power=12.0):
        vector = geometry.simple_vector(direction, power)
        self.x_velocity = vector[0]
        self.y_velocity = vector[1]

    def launch_towards(self, position, power=12.0):
        angle = geometry.angle_between(self.position, position)
        self.launch(angle, power)
