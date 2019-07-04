import pygame

import constants
pygame.init()

TAHOMA = pygame.font.SysFont("Tahoma", 10)


def debug(surface, line, *args):
    string = ""
    for arg in args:
        string += repr(arg) + " "
    text = TAHOMA.render(string, False, (255, 255, 255), (0, 0, 0))
    surface.blit(text, (10, line * 10 + 10))


def debug_line(surface, point1, point2):
    pygame.draw.line(surface, constants.RED, point1, point2)
