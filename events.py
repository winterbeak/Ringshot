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
        self.key_pressed = None


def update():
    mouse.clicked = False
    mouse.released = False
    mouse.position = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse.held = True
            mouse.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse.held = False
            mouse.released = True

        elif event.type == pygame.KEYDOWN:
            keys.key_pressed = event.key

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


mouse = MouseHandler()
keys = KeyHandler()
