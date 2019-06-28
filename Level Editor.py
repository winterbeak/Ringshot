import pygame
import sys

import graphics
import level
import constants


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

LEVELS_PER_PAGE = 5
LEVEL_BUTTON_SPACE = 60  # vertical space a button takes up, including margins

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
    width = SCREEN_WIDTH - 70
    height = 60
    button = Button((position[0], position[1], width, height))

    thumbnail_position = (SCREEN_WIDTH - 120, 0)
    thumbnail_level.draw_thumbnail(button.sprite, thumbnail_position)

    return button


def new_level():
    file = open("levels.txt", 'a')
    string = "*" + level.Level().to_string()
    file.write(string)
    file.close()


def update_levels():
    global menu_buttons
    menu_buttons = menu_buttons[0 : MENU_FIRST_LEVEL]

    file = open("levels.txt", 'r')

    levels = file.read().split('*')
    levels.pop(0)

    y = LEVEL_BUTTON_SPACE
    for level_num, level_string in enumerate(levels):
        this_level = level.string_to_level(level_string)

        level_button = create_level_button((20, y), this_level)
        if level_num // LEVELS_PER_PAGE != menu_page:
            level_button.hidden = True
        menu_buttons.append(level_button)

        y %= LEVEL_BUTTON_SPACE * LEVELS_PER_PAGE
        y += LEVEL_BUTTON_SPACE

    file.close()


def save_level(updated_level, level_num):
    file = open("levels.txt", 'r')
    levels = file.read().split('*')
    levels.pop(0)
    file.close()

    levels[level_num] = updated_level.to_string()
    string = '*'.join(levels)

    file = open("levels.txt", 'w')
    file.write(string)
    file.close()


menu_page = 0
menu_buttons = [Button((SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 10, 20, 20)),
                Button((SCREEN_WIDTH // 2 - 10, 20, 20, 20)),
                Button((SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40, 20, 20))]
MENU_SPECIAL_BUTTONS = 3
MENU_ADD = 0
MENU_UP = 1
MENU_DOWN = 2
MENU_FIRST_LEVEL = 3


def next_page():
    """Hides the current page's levels, and shows the next page's levels."""
    start = menu_page * LEVELS_PER_PAGE + MENU_SPECIAL_BUTTONS
    end = (menu_page + 1) * LEVELS_PER_PAGE + MENU_SPECIAL_BUTTONS

    for button_id in range(start, end):
        menu_buttons[button_id].hidden = True

        if button_id + LEVELS_PER_PAGE < len(menu_buttons):
            menu_buttons[button_id + LEVELS_PER_PAGE].hidden = False


def previous_page():
    """Hides the current page's levels, and shows the previous page's levels."""
    start = menu_page * LEVELS_PER_PAGE + MENU_SPECIAL_BUTTONS
    end = (menu_page + 1) * LEVELS_PER_PAGE + MENU_SPECIAL_BUTTONS

    for button_id in range(start, end):
        if button_id < len(menu_buttons):
            menu_buttons[button_id].hidden = True

        menu_buttons[button_id - LEVELS_PER_PAGE].hidden = False


def last_page():
    total_levels = len(menu_buttons) - MENU_SPECIAL_BUTTONS

    if total_levels == 0:
        return 0
    return (total_levels - 1) // LEVELS_PER_PAGE


def menu_frame():
    global current_screen
    global menu_page

    mouse_pos = pygame.mouse.get_pos()
    mouse_release = False
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_release = True

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for button_id, button in enumerate(menu_buttons):
        if button.touches_point(mouse_pos) and not button.hidden:
            if mouse_release:
                if button_id == MENU_ADD:
                    new_level()
                    menu_page = last_page()
                    update_levels()

                elif button_id == MENU_UP:
                    if menu_page > 0:
                        previous_page()
                        menu_page -= 1

                elif button_id == MENU_DOWN:
                    if menu_page < last_page():
                        next_page()
                        menu_page += 1

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