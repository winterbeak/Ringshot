import pygame

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
        self.balls = [ball.Ball(constants.SCREEN_MIDDLE, 10)]
        self.player = self.balls[0]

        # make sure you DONT DRAW THE BUTTONS on block_surface
        self.block_surface = graphics.new_surface(constants.SCREEN_SIZE)

        self.start_position = constants.SCREEN_MIDDLE

    def update(self):
        events.update()

        mouse = events.mouse
        keys = events.keys

        if mouse.held:
            if mouse.clicked:
                self.slowmo_factor = self.SLOWMO_MAX

            if self.slowmo_factor > 1.0:
                self.slowmo_factor -= self.SPEEDUP_FACTOR

                if self.slowmo_factor < 1.0:
                    self.slowmo_factor = 1.0

            self.player.rotate_towards(mouse.position, self.slowmo_factor)

        if mouse.released:
            new_ball = ball.Ball(self.player.position, self.player.radius - 1)
            old_ball = self.player
            new_ball.angle = old_ball.angle
            self.player = new_ball
            self.balls.append(new_ball)

            self.player.launch_towards(mouse.position)
            old_ball.x_velocity = -self.player.x_velocity
            old_ball.y_velocity = -self.player.y_velocity
            self.slowmo_factor = 1.0

        if keys.pressed_key == pygame.K_r:
            self.reset_level()

        for ball_ in self.balls:
            ball_.check_collision(self.level, self.slowmo_factor)
            ball_.update_body(self.slowmo_factor)

    def draw(self, surface):
        surface.blit(self.block_surface, (0, 0))
        for ball_ in self.balls:
            if ball_ is self.player:
                ball_.draw_debug(surface, constants.YELLOW)
            else:
                ball_.draw_debug(surface)

    def reset_level(self):
        self.balls = [ball.Ball(self.start_position, 10)]
        self.player = self.balls[0]

    def load_level(self, level_num):
        self.level = levels.load_level(level_num)

        block_layer = levels.LAYER_BLOCKS
        self.level.draw_debug_layer(self.block_surface, block_layer, (0, 0))

        start_tile = self.level.start_tile
        self.start_position = levels.middle_pixel(start_tile)
        self.player.goto(self.start_position)


play_screen = PlayScreen()
play_screen.load_level(1)

while True:
    play_screen.update()
    play_screen.draw(final_display)

    debug.debug(final_display, 0, clock.get_fps())
    debug.debug(final_display, 1, play_screen.player.x_velocity, play_screen.player.y_velocity)
    debug.debug(final_display, 2, play_screen.player.angle)

    screen_update(60)
