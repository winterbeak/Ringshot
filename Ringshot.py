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
        self.player = ball.Ball(constants.SCREEN_MIDDLE, 8)

        # make sure you DONT DRAW THE BUTTONS on block_surface
        self.block_surface = graphics.new_surface(constants.SCREEN_SIZE)

    def update(self):
        events.update()

        if events.mouse.held:
            if events.mouse.clicked:
                self.slowmo_factor = self.SLOWMO_MAX

            if self.slowmo_factor > 1.0:
                self.slowmo_factor -= self.SPEEDUP_FACTOR

                if self.slowmo_factor < 1.0:
                    self.slowmo_factor = 1.0

        if events.mouse.released:
            self.player.launch_towards(events.mouse.position)
            self.slowmo_factor = 1.0

        self.player.check_collision(self.level, self.slowmo_factor)
        self.player.update_body(self.slowmo_factor)

    def draw(self, surface):
        surface.blit(self.block_surface, (0, 0))
        self.player.draw_debug(surface)

    def load_level(self, level_num):
        self.level = levels.load_level(level_num)

        block_layer = levels.LAYER_BLOCKS
        self.level.draw_debug_layer(self.block_surface, block_layer, (0, 0))


play_screen = PlayScreen()
play_screen.load_level(1)

while True:
    play_screen.update()
    play_screen.draw(final_display)

    debug.debug(final_display, 0, clock.get_fps())
    debug.debug(final_display, 1, play_screen.player.x_velocity, play_screen.player.y_velocity)
    point1 = (play_screen.player.x, play_screen.player.y)
    point2 = (point1[0] + play_screen.player.x_velocity, point1[1] + play_screen.player.y_velocity)
    debug.debug_line(final_display, point1, point2)
    # if events.mouse.held:
        # screen_update(5)
    # else:
    screen_update(60)
