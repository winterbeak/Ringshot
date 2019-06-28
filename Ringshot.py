import sys
import pygame

import constants
import ball
import events


def screen_update():
    pygame.display.flip()
    final_display.fill(constants.BLACK)
    clock.tick(constants.FPS)


pygame.init()
final_display = pygame.display.set_mode(constants.SCREEN_SIZE)
clock = pygame.time.Clock()

player = ball.Ball(constants.SCREEN_MIDDLE, 8)

mouse_held = False
mouse_click = False
mouse_release = False

slowmo_factor = 1.0  # the coefficient of time-slow.  inverse of game speed
SLOWMO_MAX = 8.0  # the largest factor of slowmo possible
SPEEDUP_FACTOR = 0.05  # how much the slowmo effect "wears off" each frame

while True:
    events.update()

    if events.mouse.held:
        if events.mouse.clicked:
            slowmo_factor = SLOWMO_MAX

        if slowmo_factor > 1.0:
            slowmo_factor -= SPEEDUP_FACTOR

            if slowmo_factor < 1.0:
                slowmo_factor = 1.0

    if events.mouse.released:
        player.launch_towards(events.mouse.position)
        slowmo_factor = 1.0

    player.update_body(slowmo_factor)

    player.draw_debug(final_display)
    screen_update()
