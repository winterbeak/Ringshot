import sound

import pygame
import copy
import os
import sys

import constants
import events
import graphics
import random
import debug

import ball
import levels


def screen_update(fps):
    pygame.display.flip()
    final_display.fill(constants.BLACK)
    clock.tick(fps)


os.environ["SDL_VIDEO_CENTERED"] = "1"

# leave some pixels as a border, so it's less likely to click off the window
FULL_WIDTH = constants.FULL_WIDTH
FULL_HEIGHT = constants.FULL_HEIGHT
FULL_SIZE = constants.FULL_SIZE

SCREEN_LEFT = constants.SCREEN_LEFT
SCREEN_TOP = constants.SCREEN_TOP
TOP_LEFT = constants.SCREEN_TOP_LEFT

pygame.init()
final_display = pygame.display.set_mode(FULL_SIZE)
clock = pygame.time.Clock()

mouse_held = False
mouse_click = False
mouse_release = False

sound_transition = sound.load("transition")

LAST_LEVEL = levels.count_levels() - 1


class MenuScreen:
    def __init__(self):
        self.switch_to_level = False


class PlayScreen:
    SLOWMO_MAX = 8.0  # the largest factor of slowmo possible
    SPEEDUP_FACTOR = 0.05  # how much the slowmo effect "wears off" each frame

    def __init__(self):
        self.level = None
        self.slowmo_factor = 1.0  # the coefficient of time-slow.
        self.balls = []
        self.player = None
        self.start_ball = None
        self.level_num = 0

        # make sure you DONT DRAW THE BUTTONS on block_surface
        self.block_surface = graphics.new_surface(constants.SCREEN_SIZE)

        self.start_position = constants.SCREEN_MIDDLE
        self.end_open = False

        self.transition = False
        self.end_ball = None

        self.unlocked = True

    def update(self):
        mouse = events.mouse
        new_x = mouse.position[0] - SCREEN_LEFT
        new_y = mouse.position[1] - SCREEN_TOP
        mouse.position = (new_x, new_y)
        keys = events.keys

        if mouse.held and self.player.containing_shells:
            if mouse.clicked:
                self.slowmo_factor = self.SLOWMO_MAX

            if self.slowmo_factor > 1.0:
                self.slowmo_factor -= self.SPEEDUP_FACTOR

                if self.slowmo_factor < 1.0:
                    self.slowmo_factor = 1.0

            self.player.rotate_towards(mouse.position, self.slowmo_factor)

        if mouse.released and self.player.containing_shells:
            self.shoot_ball(mouse.position)
            self.slowmo_factor = 1.0

        if keys.pressed_key == pygame.K_r:
            if mouse.held:
                self.reset_level(True)
            else:
                self.reset_level(False)

        ball_index = len(self.balls)
        for ball_ in reversed(self.balls):
            ball_index -= 1
            if ball_.out_of_bounds():
                del self.balls[ball_index]
            else:
                ball_.check_collision(self.level, self.slowmo_factor)

                if self.level.pressed_buttons == self.level.total_buttons:
                    if ball_.touching_end:
                        self.transition = True
                        self.end_ball = ball_

                ball_.update_body(self.slowmo_factor)

        if not self.unlocked:
            if self.level.pressed_buttons == self.level.total_buttons:
                self.unlocked = True
                self.level.draw_debug_start_end(self.block_surface, (0, 0))

        graphics.update_ripples(self.slowmo_factor)

    def shoot_ball(self, position):
        """Shoots a ball towards a specified position."""
        old_ball = self.player

        new_radius = self.player.radius - ball.SHELL_WIDTH
        new_shell = old_ball.containing_shells[0]
        new_ball = ball.Ball(self.player.position, new_radius, new_shell)

        new_ball.is_player = True
        old_ball.is_player = False

        new_ball.angle = old_ball.angle
        new_ball.containing_shells = old_ball.containing_shells[1:]
        old_ball.containing_shells = []

        self.player = new_ball
        self.balls.append(new_ball)

        self.player.launch_towards(position)
        old_ball.x_velocity = -self.player.x_velocity
        old_ball.y_velocity = -self.player.y_velocity

    def draw(self, surface):
        surface.blit(self.block_surface, TOP_LEFT)
        self.level.draw_debug_layer(surface, levels.LAYER_BUTTONS, TOP_LEFT)

        graphics.draw_ripples(surface)

        for ball_ in self.balls:
            ball_.draw_debug(surface, TOP_LEFT)

    def reset_level(self, slowmo=False):
        self.balls = [copy.deepcopy(self.start_ball)]
        self.player = self.balls[0]
        columns = levels.WIDTH
        rows = levels.HEIGHT
        self.level.pressed_grid = [[False] * rows for _ in range(columns)]
        self.level.pressed_buttons = 0
        self.unlocked = False
        self.level.draw_debug_start_end(self.block_surface, (0, 0))
        if slowmo:
            self.slowmo_factor = self.SLOWMO_MAX

    def load_level(self, level_num):
        self.block_surface.fill(constants.TRANSPARENT)
        self.slowmo_factor = 1.0

        self.level_num = level_num
        self.level = levels.load_level(level_num)

        block_layer = levels.LAYER_BLOCKS
        self.level.draw_debug_layer(self.block_surface, block_layer, (0, 0))
        self.level.draw_debug_start_end(self.block_surface, (0, 0))

        start_tile = self.level.start_tile
        position = levels.middle_pixel(start_tile)
        radius = ball.first_ball_radius(self.level)
        containing_shells = self.level.start_shells
        shell = containing_shells.pop(0)

        self.start_ball = ball.Ball(position, radius, shell)
        self.start_ball.is_player = True
        self.start_ball.containing_shells = containing_shells

        self.reset_level()


class LevelTransition:
    PAUSE_LENGTH = 30
    OUT_LENGTH = 60
    IN_LENGTH = 60
    SHELL_LENGTH = 13

    PAUSE_LAST = PAUSE_LENGTH
    OUT_LAST = PAUSE_LAST + OUT_LENGTH
    IN_LAST = OUT_LAST + IN_LENGTH

    LAST_RADIUS = 700
    LAST_WIDTH = 150

    def __init__(self):
        self.previous_surface = graphics.new_surface(constants.FULL_SIZE)
        self.new_surface = graphics.new_surface(constants.FULL_SIZE)

        self.from_point = (0.0, 0.0)
        self.to_point = (0.0, 0.0)
        self.center = (0.0, 0.0)

        self.x_change = 0.0
        self.y_change = 0.0

        # finds the value a in y = a(x - r)(x - s) form
        # x and y are based off of the vertex, at maximum radius/width
        denominator = (self.OUT_LAST - self.PAUSE_LAST)
        denominator *= (self.OUT_LAST - self.IN_LAST)

        self.radius_a = self.LAST_RADIUS / denominator
        self.width_a = self.LAST_WIDTH / denominator

        self.frame = 0
        self.radius = 0.0
        self.width = 0.0

        self.transparency_temp = graphics.new_surface(FULL_SIZE)

        self.end_ball = None
        self.new_ball = None
        self.shell_count = 0
        self.color = constants.WHITE

        self.done = False

        self.sound_grow_shell = sound.load_numbers("grow_shell%i", 10)
        self.sound_grow_shell.set_volumes(0.3)

        self.sound_whoosh = sound.load("transition")
        self.sound_whoosh.set_volume(0.7)

    def update(self):
        if self.frame <= self.PAUSE_LAST:
            pass
        elif self.frame <= self.IN_LAST:
            center_x = self.center[0] + self.x_change
            center_y = self.center[1] + self.y_change
            self.center = (center_x, center_y)

            # equation is the (x - r)(x - s) part.
            equation = self.frame - self.PAUSE_LAST
            equation *= self.frame - self.IN_LAST
            self.radius = self.radius_a * equation
            self.width = self.width_a * equation

        else:
            if (self.frame - self.IN_LAST) % self.SHELL_LENGTH == 0:
                self.shell_count += 1

                if self.shell_count > len(self.new_ball.containing_shells) + 1:
                    self.done = True
                else:
                    self.sound_grow_shell.play(self.shell_count - 2)

        if self.frame == self.PAUSE_LAST:
            self.sound_whoosh.play()

        self.frame += 1

    def draw(self, surface):
        if self.frame <= self.PAUSE_LAST:
            surface.blit(self.previous_surface, (0, 0))

        elif self.frame <= self.OUT_LAST:
            shake_position = (random.randint(-3, 3), random.randint(-3, 3))
            surface.blit(self.previous_surface, shake_position)

            center = (int(self.center[0]), int(self.center[1]))
            radius = int(self.radius)
            width = int(self.width)
            pygame.draw.circle(surface, self.color, center, radius, width)

        elif self.frame <= self.IN_LAST:
            shake_position = (random.randint(-3, 3), random.randint(-3, 3))
            surface.blit(self.previous_surface, shake_position)

            center = (int(self.center[0]), int(self.center[1]))
            radius = int(self.radius)
            width = int(self.width)

            self.transparency_temp.fill(constants.BLACK)
            self.transparency_temp.blit(self.new_surface, (0, 0))
            color = constants.TRANSPARENT
            pygame.draw.circle(self.transparency_temp, color, center, radius)

            surface.blit(self.transparency_temp, shake_position)

            pygame.draw.circle(surface, self.color, center, radius, width)

        else:
            surface.blit(self.new_surface, (0, 0))
            self.new_ball.draw_debug(surface, TOP_LEFT, self.shell_count)

    def set_from_point(self, position):
        self.from_point = (position[0] + SCREEN_LEFT, position[1] + SCREEN_TOP)

    def set_to_point(self, position):
        self.to_point = (position[0] + SCREEN_LEFT, position[1] + SCREEN_TOP)

    def init_animation(self):
        """
        Initializes the circle transition.

        from_point is the first point.
        to_point is the
        Rearranging a quadratic in vertex form:
        (y - c) / ((x - d) ** 2) = a
        y is the first value
        c is the final value
        x is the first frame (0)
        d is the last frame
        """
        length = (self.OUT_LENGTH + self.IN_LENGTH)
        self.x_change = (self.to_point[0] - self.from_point[0]) / length
        self.y_change = (self.to_point[1] - self.from_point[1]) / length
        self.center = self.from_point

        self.color = ball.SHELL_DEBUG_COLORS[self.end_ball.shell_type]

        self.shell_count = 1


play_screen = PlayScreen()
file = open("Starting Level.txt", 'r')
play_screen.load_level(int(file.readline()))
file.close()

transition = LevelTransition()

PLAY = 0
TRANSITION = 1
current_screen = PLAY

while True:
    events.update()
    sound.update()

    if current_screen == PLAY:
        play_screen.update()
        play_screen.draw(final_display)

        if play_screen.transition:
            play_screen.transition = False
            transition.frame = 0

            transition.previous_surface.fill(constants.TRANSPARENT)
            transition.previous_surface.blit(final_display, (0, 0))
            transition.end_ball = play_screen.end_ball

            transition.new_surface.fill(constants.TRANSPARENT)

            if play_screen.level_num != LAST_LEVEL:
                play_screen.load_level(play_screen.level_num + 1)
                play_screen.level.draw_debug(transition.new_surface, TOP_LEFT)
                transition.new_ball = play_screen.player
                transition.set_to_point(play_screen.player.position)

            else:
                transition.set_to_point(constants.SCREEN_MIDDLE)
                play_screen.level_num += 1

            transition.set_from_point(transition.end_ball.position)

            transition.init_animation()

            current_screen = TRANSITION

            sound.play(ball.end_note, 0.5)

    elif current_screen == TRANSITION:
        transition.update()

        if transition.frame == transition.IN_LAST:
            if play_screen.level_num == LAST_LEVEL + 1:
                for frame in range(60):
                    events.update()
                    screen_update(60)
                pygame.quit()
                sys.exit()

        transition.draw(final_display)

        if transition.done:
            transition.done = False
            current_screen = PLAY
            graphics.clear_ripples()

    debug.debug(clock.get_fps())
    debug.draw(final_display)

    screen_update(60)
