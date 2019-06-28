import pygame
import sys

import graphics
import levels
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


def small_button(position):
    width = 20
    height = 20
    return Button((position[0], position[1], width, height))


def create_level_button(position, thumbnail_level, level_num):
    width = SCREEN_WIDTH - 70
    height = 60
    button = Button((position[0], position[1], width, height))

    thumbnail_position = (SCREEN_WIDTH - 120, 0)
    thumbnail_level.draw_thumbnail(button.sprite, thumbnail_position)

    text = TAHOMA.render(str(level_num), False, constants.WHITE)
    button.sprite.blit(text, (10, 10))

    return button


class MainMenu:
    def __init__(self):
        self.SPECIAL_BUTTONS = 3
        self.ADD = 0
        self.UP = 1
        self.DOWN = 2
        self.FIRST_LEVEL = 3
        self.LEVELS_PER_PAGE = 5
        self.LEVEL_BUTTON_SPACE = 60

        self.buttons = [small_button((SCREEN_WIDTH - 40, SCREEN_HEIGHT//2 - 10)),
                        small_button((SCREEN_WIDTH // 2 - 10, 20)),
                        small_button((SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40))]

        self.page = 0
        self.last_page = (levels.count_levels() - 1) // self.LEVELS_PER_PAGE

        self.level_clicked = -1
        self.switch_to_editor = False

    def update_frame(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_release = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_release = True

            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        for button_id, button in enumerate(self.buttons):
            if button.touches_point(mouse_pos) and not button.hidden:
                if mouse_release:
                    if button_id == self.ADD:
                        levels.make_new_level()
                        self.change_page(self.last_page)
                        self.update_level_buttons()

                    elif button_id == self.UP:
                        if self.page > 0:
                            self.change_page(self.page - 1)
                        else:
                            self.change_page(self.last_page)

                    elif button_id == self.DOWN:
                        if self.page < self.last_page:
                            self.change_page(self.page + 1)
                        else:
                            self.change_page(0)

                    elif button_id >= self.FIRST_LEVEL:
                        self.switch_to_editor = True
                        self.level_clicked = button_id
                        return

                button.highlight = True
            else:
                button.highlight = False

            button.draw(final_display)

    def change_page(self, page):
        """Switches the menu page to the specified page."""
        self.page = page

        first_button = self.page * self.LEVELS_PER_PAGE + self.SPECIAL_BUTTONS
        last_button = first_button + self.LEVELS_PER_PAGE - 1

        for button_id in range(self.FIRST_LEVEL, len(self.buttons)):
            if first_button <= button_id <= last_button:
                self.buttons[button_id].hidden = False
            else:
                self.buttons[button_id].hidden = True

    def update_level_buttons(self):
        """Reloads all the level buttons, even those not on the current page."""
        self.buttons = self.buttons[0:self.FIRST_LEVEL]

        file = open("levels.txt", 'r')
        level_array = file.read().split('*')
        level_array.pop(0)
        file.close()

        y = self.LEVEL_BUTTON_SPACE
        for level_num, level_string in enumerate(level_array):
            this_level = levels.string_to_level(level_string)

            level_button = create_level_button((20, y), this_level, level_num)
            if level_num // self.LEVELS_PER_PAGE != self.page:
                level_button.hidden = True
            self.buttons.append(level_button)

            y %= self.LEVEL_BUTTON_SPACE * self.LEVELS_PER_PAGE
            y += self.LEVEL_BUTTON_SPACE

        self.last_page = (levels.count_levels() - 1) // self.LEVELS_PER_PAGE


holding_block = levels.EMPTY
level_surface = graphics.new_surface(SCREEN_SIZE)


def editor_frame():
    global holding_block

    number_pressed = -1
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_release = True

        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name.isnumeric():
                number_pressed = int(key_name)

        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if 0 <= number_pressed < levels.BLOCK_TYPES:
        holding_block = number_pressed

    final_display.blit(level_surface, (0, 0))


main_menu = MainMenu()
main_menu.update_level_buttons()
main_menu.change_page(main_menu.last_page)

MENU = 0
EDITOR = 1

current_screen = MENU
editor_level = None
editor_level_num = 0
while True:
    if current_screen == MENU:
        main_menu.update_frame()

        if main_menu.switch_to_editor:
            current_screen = EDITOR
            editor_level_num = main_menu.level_clicked - 3
            editor_level = levels.load_level(editor_level_num)

            level_surface = graphics.new_surface(SCREEN_SIZE)
            editor_level.draw_debug(level_surface, (0, 0))

    elif current_screen == EDITOR:
        editor_frame()

    screen_update()
