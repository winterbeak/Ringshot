import pygame
import sys

import graphics
import level
import constants


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

pygame.init()
final_display = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

TAHOMA = pygame.font.SysFont("Tahoma", 10)


def screen_update():
    pygame.display.flip()
    final_display.fill(constants.BLACK)
    clock.tick(constants.FPS)


class Button:
    OUTLINE_COLOR = constants.WHITE
    HIGHLIGHT_COLOR = (100, 100, 100)

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]

        self.sprite = graphics.new_surface((self.w, self.h))
        graphics.border(self.sprite, self.OUTLINE_COLOR, 2)
        self.hidden = False

        self.highlight = False

    def touches_point(self, point):
        if self.rect.collidepoint(point[0], point[1]):
            return True
        return False

    def draw(self, surface):
        if not self.hidden:
            if self.highlight:
                pygame.draw.rect(surface, self.HIGHLIGHT_COLOR, self.rect)
            surface.blit(self.sprite, (self.x, self.y))


def create_level_button(position, thumbnail_level):
    button = Button((position[0], position[1], SCREEN_WIDTH - 70, 70))

    thumbnail_position = (SCREEN_WIDTH - 120, 0)
    thumbnail_level.draw_thumbnail(button.sprite, thumbnail_position)

    return button


def new_level():
    file = open("levels.txt", 'a')
    string = "*" + level.Level().to_string()
    file.write(string)
    file.close()


def update_levels():
    file = open("levels.txt", 'r')

    levels = file.read().split('*')
    levels.pop(0)

    y = 80
    for level_string in levels:
        this_level = level.string_to_level(level_string)
        menu_buttons.append(create_level_button((20, y), this_level))

        y = (y % 400) + 80


menu_page = 0
menu_buttons = [Button((SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 10, 20, 20)),
                Button((SCREEN_WIDTH // 2 - 10, 20, 20, 20)),
                Button((SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40, 20, 20))]
MENU_ADD = 0
MENU_PREV = 1
MENU_NEXT = 2


def menu_frame():
    global current_screen

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    mouse_release = False
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_release = True

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for button_id, button in enumerate(menu_buttons):
        if button.touches_point(mouse_pos):
            if mouse_release:
                if button_id == MENU_ADD:
                    new_level()
                    update_levels()

            button.highlight = True
        else:
            button.highlight = False

        button.draw(final_display)


update_levels()
MENU = 0

current_screen = MENU
while True:
    if current_screen == MENU:
        menu_frame()
    screen_update()