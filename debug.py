import pygame
pygame.init()

TAHOMA = pygame.font.SysFont("Tahoma", 10)


def debug(surface, line, *args):
    string = ""
    for arg in args:
        string += repr(arg) + " "
    text = TAHOMA.render(string, False, (255, 255, 255), (0, 0, 0))
    surface.blit(text, (10, line * 10 + 10))
