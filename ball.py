import sound

import pygame
import math

import constants
import geometry
import levels
import graphics
# import debug

# each "layer" of the ball is called a shell.
SHELL_TYPES = 4
CENTER = 0  # the ball at the very center, cannot be shot
NORMAL = 1  # the normal, 100% tangible shell type
GHOST = 2  # the paranormal, 0% tangible shell type
FLOAT = 3  # the futuristic, 0% gravity shell type
CLONE = 4  # the frankly kinda odd, 200% shell type
SHELL_DEBUG_COLORS = (constants.WHITE, constants.MAGENTA, constants.GREEN,
                      constants.ORANGE, constants.CYAN)

MAX_SHELLS = 10

SMALLEST_RADIUS = 6  # the radius of the smallest, innermost ball
SHELL_WIDTH = 2

sound_button = sound.load_numbers("button%i", 3)


def first_ball_radius(level):
    return (len(level.start_shells) - 1) * SHELL_WIDTH + SMALLEST_RADIUS


class Ball:
    """A simulated ball that experiences gravity and rolls."""
    DEBUG_COLOR = constants.MAGENTA
    BLIP_COLOR = constants.CYAN
    CHECK_STEPS = 8  # how many intermediate frames to check between frames
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
        self.FLOATING_BOUNCE_DECAY = min(0.9, self.NORMAL_BOUNCE_DECAY + 0.2)
        self.x_bounce_decay = bounce_decay
        self.y_bounce_decay = bounce_decay

        self.is_player = False
        self.containing_shells = None
        self.shell_type = shell_type

        self.touching_end = False

        self.ghost_ripple_timer = 0.0
        self.GHOST_RIPPLE_DELAY = 5.0

    def draw_debug(self, surface, screen_top_left=(0, 0), shells=0):
        x = int(self.x)  # pygame circles use integers
        y = int(self.y)
        position = (x + screen_top_left[0], y + screen_top_left[1])

        radius = self.radius
        if self.is_player:
            if shells == 0 or shells > len(self.containing_shells):
                color = SHELL_DEBUG_COLORS[self.shell_type]
                pygame.draw.circle(surface, color, position, radius)

                for shell in self.containing_shells:
                    radius -= SHELL_WIDTH
                    color = SHELL_DEBUG_COLORS[shell]
                    pygame.draw.circle(surface, color, position, radius)

                radius = self.radius
            else:
                first_shell = len(self.containing_shells) - shells

                radius -= first_shell * SHELL_WIDTH

                for shell in self.containing_shells[first_shell:]:
                    radius -= SHELL_WIDTH
                    color = SHELL_DEBUG_COLORS[shell]
                    pygame.draw.circle(surface, color, position, radius)

                radius = self.radius - ((first_shell + 1) * SHELL_WIDTH)

            blip_distance = geometry.vector_to_difference(self.angle, radius - 1)
            blip_x = int(self.x + blip_distance[0] + screen_top_left[0])
            blip_y = int(self.y + blip_distance[1] + screen_top_left[1])

            pygame.draw.line(surface, self.BLIP_COLOR, position, (blip_x, blip_y), 2)

        else:
            color = SHELL_DEBUG_COLORS[self.shell_type]
            pygame.draw.circle(surface, color, position, radius, 1)

            blip_distance = geometry.vector_to_difference(self.angle, radius - 1)
            blip_x = int(self.x + blip_distance[0] + screen_top_left[0])
            blip_y = int(self.y + blip_distance[1] + screen_top_left[1])
            surface.fill(self.BLIP_COLOR, (blip_x, blip_y, 2, 2))

    def draw_debug_arc(self, surface, screen_top_left=(0, 0), shells=0):
        """Draws the shells as arcs rather than circles (so that they have
        an opening on one side to 'shoot' the ball out of).  Doesn't
        look as good because the arcs don't fill well, so this doesn't
        get used.
        """
        x = int(self.x) + screen_top_left[0]
        y = int(self.y) + screen_top_left[1]

        radius = self.radius
        width = SHELL_WIDTH
        start = -self.angle + 0.5
        end = -self.angle - 0.5
        if self.is_player:
            if shells == 0 or shells > len(self.containing_shells):
                color = SHELL_DEBUG_COLORS[self.shell_type]
                rect = (x - radius, y - radius, radius * 2, radius * 2)

                pygame.draw.arc(surface, color, rect, start, end, width)

                for shell in self.containing_shells[:-1]:
                    radius -= SHELL_WIDTH
                    color = SHELL_DEBUG_COLORS[shell]
                    rect = (x - radius, y - radius, radius * 2, radius * 2)

                    pygame.draw.arc(surface, color, rect, start, end, width)

                radius -= SHELL_WIDTH
                color = SHELL_DEBUG_COLORS[CENTER]
                pygame.draw.circle(surface, color, (x, y), radius)

            else:
                first_shell = len(self.containing_shells) - shells

                radius -= first_shell * SHELL_WIDTH

                for shell in self.containing_shells[first_shell:]:
                    radius -= SHELL_WIDTH
                    color = SHELL_DEBUG_COLORS[shell]
                    rect = (x - radius, y - radius, radius * 2, radius * 2)
                    pygame.draw.arc(surface, color, rect, start, end, width)

        else:
            rect = (x - radius, y - radius, radius * 2, radius * 2)
            color = SHELL_DEBUG_COLORS[self.shell_type]
            pygame.draw.arc(surface, color, rect, start, end, width)

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
        if not self.is_player and self.shell_type == FLOAT:
            self.y_acceleration = 0.0
        else:
            self.y_acceleration = constants.GRAVITY

        distance_x = self.x_velocity / slowmo_factor
        distance_y = self.y_velocity / slowmo_factor
        self.move((distance_x, distance_y))

        self.x_velocity += self.x_acceleration / slowmo_factor
        self.y_velocity += self.y_acceleration / slowmo_factor

        self.angle += self.angular_velocity / slowmo_factor

        if not self.is_player and self.shell_type == FLOAT:
            self.x_velocity *= 0.993 + min(0.0065, 0.0015 * slowmo_factor)
            self.y_velocity *= 0.993 + min(0.0065, 0.0015 * slowmo_factor)
            self.angular_velocity *= 0.98 + min(0.01, 0.00075 * slowmo_factor)

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
        ghost_ripple = False

        full_step = self.next_position(slowmo_factor)
        for step in range(1, self.CHECK_STEPS + 1):
            multiplier = step / self.CHECK_STEPS

            delta_x = (full_step[0] - self.x) * multiplier
            delta_y = (full_step[1] - self.y) * multiplier

            next_position = (self.x + delta_x, self.y + delta_y)

            radius = self.radius
            if self.shell_type == GHOST and self.is_player:
                for shell in self.containing_shells:
                    if shell != GHOST:
                        break
                    radius -= SHELL_WIDTH

            tiles = levels.tiles_touching_ball(radius, next_position)
            shortest_segment = None
            shortest = 1000000.0
            for tile in tiles:
                if not tile:  # remember, out of bounds tiles return None
                    continue

                if tile == level.end_tile:
                    self.touching_end = True

                if level.is_button(tile) and not level.is_pressed(tile):
                    level.press(tile)
                    level.button_ripple(tile)
                    sound_button.play_random()

                segments = level.tile_to_segments(tile)
                if not segments:
                    continue
                elif self.shell_type == GHOST and not self.is_player:
                    ghost_ripple = True
                    continue

                for segment in segments:
                    new_segment = geometry.point_and_segment(next_position, segment)
                    if new_segment and new_segment.length < shortest:
                        shortest_segment = new_segment
                        shortest = new_segment.length

            if shortest_segment and shortest < radius:
                shortest_segment.slope = -shortest_segment.slope

                velocity = (self.x_velocity, -self.y_velocity)
                perpendicular = -geometry.inverse(shortest_segment.slope)
                reflected = geometry.reflect_vector(perpendicular, velocity)
                # print(velocity)
                # print(reflected)
                # print()

                self.update_angular_velocity(perpendicular)

                # velocity stuff
                # y is negative since up is negative and down is positive!
                # pygame sure is weird.
                new_velocity_x = reflected[0] * self.x_bounce_decay
                new_velocity_y = -reflected[1] * self.y_bounce_decay

                self.x_velocity = new_velocity_x
                self.y_velocity = new_velocity_y

                magnitude = geometry.magnitude((new_velocity_x, new_velocity_y))

                if self.is_player and self.shell_type == GHOST:
                    for shell in self.containing_shells:
                        if shell != GHOST:
                            shell_type = shell
                            break
                    else:
                        shell_type = CENTER
                else:
                    shell_type = self.shell_type

                if shell_type == CENTER or shell_type == NORMAL:
                    # a few checks to prevent rippling while
                    # rolling on the ground
                    flat_ground = abs(perpendicular) < 0.0001
                    grounded = abs(self.y_velocity) < self.GROUNDED_THRESHOLD
                    if magnitude > 3.0 and not (flat_ground and grounded):
                        self.ripple(magnitude * 4.0)
                        volume = (magnitude - 3.0) / 5.0 + 0.2

                        sound.normal_scale.play_random(volume, self.is_player)

                elif self.shell_type == FLOAT:
                    if magnitude > 1.0:
                        self.ripple(magnitude * 4.0)
                        volume = (magnitude - 1.0) / 5.0 + 0.2

                        sound.float_scale.play_random(volume)

                break

        # self.update_grounded(level)
        floating = not (self.is_player or self.shell_type != FLOAT)
        if not floating and abs(self.y_velocity) < self.GROUNDED_THRESHOLD:
            self.x_bounce_decay = 0.95
            self.y_bounce_decay = self.y_velocity / 2
        elif floating:
            self.x_bounce_decay = self.FLOATING_BOUNCE_DECAY
            self.y_bounce_decay = self.FLOATING_BOUNCE_DECAY
        else:
            self.x_bounce_decay = self.NORMAL_BOUNCE_DECAY
            self.y_bounce_decay = self.NORMAL_BOUNCE_DECAY

        if ghost_ripple and self.ghost_ripple_timer >= self.GHOST_RIPPLE_DELAY:
            sound.ghost_note.play()
            self.ghost_ripple_timer = 0.0
            position = graphics.screen_position(self.position)
            color = SHELL_DEBUG_COLORS[GHOST]
            graphics.create_ripple(position, color, self.radius)

        elif self.ghost_ripple_timer < self.GHOST_RIPPLE_DELAY:
            self.ghost_ripple_timer += 1.0 / slowmo_factor

    def out_of_bounds(self):
        position = graphics.screen_position(self.position)
        if -100 <= position[0] < constants.FULL_WIDTH + 100:
            if -100 <= position[1] < constants.FULL_HEIGHT + 100:
                return False
        return True

    def ripple(self, radius):
        radius = radius
        color = SHELL_DEBUG_COLORS[self.shell_type]
        x = self.x + constants.SCREEN_LEFT
        y = self.y + constants.SCREEN_TOP
        graphics.create_ripple((x, y), color, radius)

    def update_angular_velocity(self, contact_slope):
        """Updates the angular velocity of the ball (how fast it spins).

        Angular velocity here is simplified to be proportional to the
        velocity of the ball parallel to the contact surface.

        Note that this is purely cosmetic and does not actually affect
        physics in any way.
        """
        velocity = (self.x_velocity, self.y_velocity)

        direction = -math.atan(contact_slope)
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

    def point_towards_end(self, level):
        end_point = levels.middle_pixel(level.end_tile)
        self.angle = geometry.angle_between(self.position, end_point)
