import pygame
import copy

import constants
import events
import graphics
import debug

import ball
import levels


def screen_update(fps):
    pygame.display.flip()
    final_display.fill(constants.BLACK)
    clock.tick(fps)


pygame.init()
final_display = pygame.display.set_mode(constants.SCREEN_SIZE)
clock = pygame.time.Clock()

mouse_held = False
mouse_click = False
mouse_release = False


class PlayScreen:
    SLOWMO_MAX = 8.0  # the largest factor of slowmo possible
    SPEEDUP_FACTOR = 0.05  # how much the slowmo effect "wears off" each frame

    def __init__(self):
        self.level = None
        self.slowmo_factor = 1.0  # the coefficient of time-slow.
        self.balls = []
        self.player = None
        self.start_ball = None

        # make sure you DONT DRAW THE BUTTONS on block_surface
        self.block_surface = graphics.new_surface(constants.SCREEN_SIZE)

        self.start_position = constants.SCREEN_MIDDLE

    def update(self):
        events.update()

        mouse = events.mouse
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
            self.reset_level()

        ball_index = len(self.balls)
        for ball_ in reversed(self.balls):
            ball_index -= 1
            if ball_.out_of_bounds():
                del self.balls[ball_index]
            else:
                ball_.check_collision(self.level, self.slowmo_factor)
                ball_.update_body(self.slowmo_factor)

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
        surface.blit(self.block_surface, (0, 0))
        for ball_ in self.balls:
            ball_.draw_debug(surface)

    def reset_level(self):
        self.balls = [copy.deepcopy(self.start_ball)]
        self.player = self.balls[0]

    def load_level(self, level_num):
        self.level = levels.load_level(level_num)

        block_layer = levels.LAYER_BLOCKS
        self.level.draw_debug_layer(self.block_surface, block_layer, (0, 0))

        start_tile = self.level.start_tile
        position = levels.middle_pixel(start_tile)
        radius = ball.first_ball_radius(self.level)
        containing_shells = self.level.start_shells
        shell = containing_shells.pop(0)

        self.start_ball = ball.Ball(position, radius, shell)
        self.start_ball.is_player = True
        self.start_ball.containing_shells = containing_shells

        self.reset_level()


play_screen = PlayScreen()
play_screen.load_level(1)
print(play_screen.player.containing_shells)

while True:
    play_screen.update()
    play_screen.draw(final_display)

    debug.debug(final_display, 0, clock.get_fps())
    debug.debug(final_display, 1, play_screen.player.x_velocity, play_screen.player.y_velocity)
    debug.debug(final_display, 2, play_screen.player.angle)
    debug.debug(final_display, 3, play_screen.balls)
    debug.debug(final_display, 4, play_screen.player.y)

    screen_update(60)
