import pygame
import math

import constants
import geometry
import levels

# each "layer" of the ball is called a shell.
SHELL_TYPES = 2
CENTER = 0  # the ball at the very center, cannot be shot
NORMAL = 1  # the normal, 100% tangible shell type
GHOST = 2  # the paranormal, 0% tangible shell type
SHELL_DEBUG_COLORS = (constants.WHITE, constants.MAGENTA, constants.CYAN)

SMALLEST_RADIUS = 6  # the radius of the smallest, innermost ball
SHELL_WIDTH = 2


def first_ball_radius(level):
    return (len(level.start_shells) - 1) * SHELL_WIDTH + SMALLEST_RADIUS


class Ball:
    """A simulated ball that experiences gravity and rolls."""
    DEBUG_COLOR = constants.MAGENTA
    BLIP_COLOR = constants.CYAN
    CHECK_STEPS = 2  # how many intermediate frames to check between frames
    GROUNDED_THRESHOLD = 1.3  # what speed to start grounding the ball at

    def __init__(self, position, radius, shell_type, bounce_decay=0.7):
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
        # self.grounded = False

        # bounce_decay is how bouncy the ball is.  value should be between
        # 0 and 1.  settting bounce decay greater than 1 is wild, though!
        # specifically, bounce_decay measures what percentage of the initial
        # speed is kept after bouncing.
        self.NORMAL_BOUNCE_DECAY = bounce_decay
        self.x_bounce_decay = bounce_decay
        self.y_bounce_decay = bounce_decay

        self.is_player = False
        self.containing_shells = None
        self.shell_type = shell_type

        self.touching_end = False

    def draw_debug(self, surface, screen_top_left=(0, 0)):
        x = int(self.x)  # pygame circles use integers
        y = int(self.y)
        position = (x + screen_top_left[0], y + screen_top_left[1])

        if self.is_player:
            radius = self.radius
            color = SHELL_DEBUG_COLORS[self.shell_type]
            pygame.draw.circle(surface, color, position, radius)

            for shell in self.containing_shells:
                radius -= SHELL_WIDTH
                color = SHELL_DEBUG_COLORS[shell]
                pygame.draw.circle(surface, color, position, radius)

        else:
            color = SHELL_DEBUG_COLORS[self.shell_type]
            pygame.draw.circle(surface, color, position, self.radius, 1)

        # draws a little pixel representing the ball's rotation
        blip_distance = geometry.vector_to_difference(self.angle, self.radius)
        blip_x = int(self.x + blip_distance[0] + screen_top_left[0])
        blip_y = int(self.y + blip_distance[1] + screen_top_left[1])
        pygame.draw.line(surface, self.BLIP_COLOR, position, (blip_x, blip_y), 3)

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

        slowmo_factor is how much the ball slows down due to slowmo.
        """
        self.y_acceleration = constants.GRAVITY

        distance_x = self.x_velocity / slowmo_factor
        distance_y = self.y_velocity / slowmo_factor
        self.move((distance_x, distance_y))

        self.x_velocity += self.x_acceleration / slowmo_factor
        self.y_velocity += self.y_acceleration / slowmo_factor

        self.angle += self.angular_velocity / slowmo_factor

    def next_position(self, slowmo_factor=1.0):
        """Returns the expected position on the next frame, without
        taking into account collision."""
        x = self.x + self.x_velocity / slowmo_factor
        y = self.y + self.y_velocity / slowmo_factor
        return x, y

    # def update_grounded(self, level):
    #     if abs(self.y_velocity) > self.GROUNDED_THRESHOLD:
    #         self.grounded = False
    #         return
    #
    #     point_below = (self.x, self.y + self.radius + self.GROUNDED_THRESHOLD)
    #     grid_position_below = levels.grid_tile_position(point_below)
    #     tile = level.layers[levels.LAYER_BLOCKS].tile_at(grid_position_below)
    #
    #     if levels.is_ground(tile):
    #         self.grounded = True
    #     else:
    #         self.grounded = False

    def check_collision(self, level, slowmo_factor=1.0):
        """Updates the player's position and velocity based on where they
        are going in the level.
        """
        self.touching_end = False

        full_step = self.next_position(slowmo_factor)
        for step in range(1, self.CHECK_STEPS + 1):
            multiplier = step / self.CHECK_STEPS

            delta_x = (full_step[0] - self.x) * multiplier
            delta_y = (full_step[1] - self.y) * multiplier

            next_position = (self.x + delta_x, self.y + delta_y)

            tiles = levels.tiles_touching_ball(self.radius, next_position)
            shortest_segment = None
            shortest = 1000000.0
            for tile in tiles:
                if not tile:  # remember, out of bounds tiles return None
                    continue

                if tile == level.end_tile:
                    self.touching_end = True

                if level.is_button(tile):
                    level.press(tile)

                segments = level.tile_to_segments(tile)
                if not segments:
                    continue

                for segment in segments:
                    new_segment = geometry.point_and_segment(next_position, segment)
                    if new_segment.length < shortest:
                        shortest_segment = new_segment
                        shortest = new_segment.length

            if shortest_segment and shortest < self.radius:
                velocity = (self.x_velocity, self.y_velocity)
                perpendicular = geometry.inverse(shortest_segment.slope)
                reflected = geometry.reflect_vector(perpendicular, velocity)

                self.update_angular_velocity(perpendicular)

                # print(shortest_segment.point1, shortest_segment.point2)
                # print(self.x_velocity, self.y_velocity)
                # print(reflected)
                # print(shortest_segment.slope)
                # print()

                # velocity stuff
                # y is negative since up is negative and down is positive!
                # pygame sure is weird.
                new_velocity_x = reflected[0] * self.x_bounce_decay
                new_velocity_y = -reflected[1] * self.y_bounce_decay
                self.x_velocity = new_velocity_x
                self.y_velocity = new_velocity_y

                break

        # self.update_grounded(level)
        if abs(self.y_velocity) < self.GROUNDED_THRESHOLD:
            self.y_bounce_decay = self.y_velocity / 2
        else:
            self.y_bounce_decay = self.NORMAL_BOUNCE_DECAY

    def out_of_bounds(self):
        if -100 <= self.x < constants.SCREEN_WIDTH + 100:
            if -100 <= self.y < constants.SCREEN_HEIGHT + 100:
                return False
        return True

    def update_angular_velocity(self, contact_slope):
        """Updates the angular velocity of the ball (how fast it spins).

        Angular velocity here is simplified to be proportional to the
        velocity of the ball parallel to the contact surface.

        Note that this is purely cosmetic and does not actually affect
        physics in any way.
        """
        velocity = (self.x_velocity, self.y_velocity)

        direction = math.atan(contact_slope)
        velocity_vector = geometry.difference_to_vector(velocity)
        magnitude = geometry.component_in_direction(velocity_vector, direction)

        self.angular_velocity = magnitude / 10

    def launch(self, direction, power=12.0):
        vector = geometry.vector_to_difference(direction, power)
        self.x_velocity = vector[0]
        self.y_velocity = vector[1]

    def launch_towards(self, position, power=12.0):
        angle = geometry.angle_between(self.position, position)
        self.launch(angle, power)

    def rotate_towards(self, position, slowmo_factor=1.0):
        """Rotate the ball to face towards a specific position.

        Does not rotate instantly.
        """
        angle = geometry.angle_between(self.position, position)
        delta_angle = angle - self.angle

        if delta_angle > math.pi:
            delta_angle = -(math.pi * 2 - delta_angle)
        elif delta_angle < -math.pi:
            delta_angle = -(-math.pi * 2 - delta_angle)

        self.angle += delta_angle / slowmo_factor

        while self.angle < -math.pi:
            self.angle += math.pi * 2

        while self.angle > math.pi:
            self.angle -= math.pi * 2
