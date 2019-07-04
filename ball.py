import pygame

import constants
import geometry
import levels


class Ball:
    """A simulated ball that experiences gravity and rolls."""
    DEBUG_COLOR = constants.MAGENTA
    BLIP_COLOR = constants.CYAN

    def __init__(self, position, radius):
        self.x = position[0]
        self.y = position[1]
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.x_acceleration = 0.0
        self.y_acceleration = 0.0
        self.position = position
        self.radius = radius
        self.angle = 0
        self.angular_velocity = 0.0

    def draw_debug(self, surface):
        position = (int(self.x), int(self.y))  # pygame circles use integers
        pygame.draw.circle(surface, self.DEBUG_COLOR, position, self.radius)

        # draws a little pixel representing the ball's rotation
        blip_distance = geometry.vector_to_delta(self.angle, self.radius)
        blip_x = int(self.x + blip_distance[0])
        blip_y = int(self.y + blip_distance[1])
        pygame.draw.circle(surface, self.BLIP_COLOR, (blip_x, blip_y), 1)

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

    def update_body(self, slowmo_factor=1.0):
        """Moves the ball according to its velocity and acceleration.  Also
        rotates it based on how much it should rotate.

        slowmo_factor is how much the ball slows down due to slowmo."""
        self.y_acceleration = constants.GRAVITY

        distance_x = self.x_velocity / slowmo_factor
        distance_y = self.y_velocity / slowmo_factor
        self.move((distance_x, distance_y))

        self.x_velocity += self.x_acceleration / slowmo_factor
        self.y_velocity += self.y_acceleration / slowmo_factor

        self.angle += self.angular_velocity / slowmo_factor

    def next_position(self, slowmo_factor = 1.0):
        """Returns the expected position on the next frame, without
        taking into account collision."""
        x = self.x + self.x_velocity / slowmo_factor
        y = self.y + self.y_velocity / slowmo_factor
        return x, y

    def check_collision(self, level, slowmo_factor = 1.0):
        """Updates the player's position and velocity based on where they
        are going in the level."""
        next_position = self.next_position(slowmo_factor)

        tiles = levels.tiles_touching_ball(self.radius, self.position)
        for tile in tiles:
            if tile:  # remember, out of bounds tiles return None
                segments = level.tile_to_segments(tile)
                for segment in segments:
                    pass


    def launch(self, direction, power=12.0):
        vector = geometry.vector_to_delta(direction, power)
        self.x_velocity = vector[0]
        self.y_velocity = vector[1]

    def launch_towards(self, position, power=12.0):
        angle = geometry.angle_between(self.position, position)
        self.launch(angle, power)
