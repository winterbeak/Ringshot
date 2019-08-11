import pygame
import sys

pygame.init()


class MouseHandler:
    def __init__(self):
        self.clicked = False
        self.released = False
        self.held = False
        self.position = (0, 0)


class KeyHandler:
    def __init__(self):
        self.pressed = False
        self.pressed_key = None


exit_program = False


def update():
    global exit_program

    mouse.clicked = False
    mouse.released = False
    mouse.position = pygame.mouse.get_pos()

    keys.pressed = False
    keys.pressed_key = None
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse.held = True
            mouse.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse.held = False
            mouse.released = True

        elif event.type == pygame.KEYDOWN:
            keys.pressed = True
            keys.pressed_key = event.key

        elif event.type == pygame.QUIT:
            exit_program = True


mouse = MouseHandler()
keys = KeyHandler()
