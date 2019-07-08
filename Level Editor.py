import pygame
import os

import graphics
import levels
import constants
import events
import ball
# import debug


os.environ["SDL_VIDEO_CENTERED"] = "1"

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
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
        self.selected = False

    def touches_point(self, point):
        if self.rect.collidepoint(point[0], point[1]):
            return True
        return False

    def draw(self, surface):
        if self.selected:
            self.highlight = True

        if not self.hidden:
            if self.highlight:
                pygame.draw.rect(surface, self.HIGHLIGHT_COLOR, self.rect)
            surface.blit(self.sprite, (self.x, self.y))


class ButtonSet:
    ARROW_LEFT = 0
    ARROW_UP = 1
    ARROW_RIGHT = 2
    ARROW_DOWN = 3

    def __init__(self):
        self.buttons = []
        self.touch_mouse = -1
        self.button_count = 0

    def draw(self, surface):
        for button in self.buttons:
            button.draw(surface)

    def update(self):
        touching_a_button = False
        for button_id, button in enumerate(self.buttons):
            button_touches = button.touches_point(events.mouse.position)
            if button_touches and not button.hidden:
                touching_a_button = True
                self.touch_mouse = button_id
                button.highlight = True
            elif not button.selected:
                button.highlight = False

        if not touching_a_button:
            self.touch_mouse = -1

    def add(self, button):
        self.buttons.append(button)
        self.button_count += 1

    def pop(self):
        self.buttons.pop()
        self.button_count -= 1

    def slice_to(self, index):
        self.buttons = self.buttons[:index]
        self.button_count = index

    def show(self, button_id):
        self.buttons[button_id].hidden = False

    def hide(self, button_id):
        self.buttons[button_id].hidden = True

    def select(self, button_id):
        self.buttons[button_id].selected = True

    def deselect(self, button_id):
        self.buttons[button_id].selected = False

    def draw_plus(self, button_id):
        surface = self.buttons[button_id].sprite

        vertical_rect = (13, 5, 4, 20)
        surface.fill(constants.WHITE, vertical_rect)

        horizontal_rect = (5, 13, 20, 4)
        surface.fill(constants.WHITE, horizontal_rect)

    def draw_minus(self, button_id):
        surface = self.buttons[button_id].sprite

        rect = (5, 13, 20, 4)
        surface.fill(constants.WHITE, rect)

    def draw_arrow(self, button_id, direction):
        surface = self.buttons[button_id].sprite

        if direction == self.ARROW_LEFT:
            points = ((5, 15), (25, 5), (25, 25))
        elif direction == self.ARROW_UP:
            points = ((15, 5), (5, 25), (25, 25))
        elif direction == self.ARROW_RIGHT:
            points = ((25, 15), (5, 5), (5, 25))
        elif direction == self.ARROW_DOWN:
            points = ((15, 25), (5, 5), (25, 5))
        else:
            return
        pygame.draw.polygon(surface, constants.WHITE, points)


def small_button(position):
    width = 30
    height = 30
    return Button((position[0], position[1], width, height))


def level_button(position, thumbnail_level, level_num):
    width = SCREEN_WIDTH - 70
    height = 60
    button = Button((position[0], position[1], width, height))

    thumbnail_position = (SCREEN_WIDTH - 120, 0)
    block_layer = thumbnail_level.layers[levels.LAYER_BLOCKS]
    block_layer.draw_thumbnail(button.sprite, thumbnail_position)

    text = TAHOMA.render(str(level_num), False, constants.WHITE)
    button.sprite.blit(text, (10, 10))

    return button


class MainMenu:
    def __init__(self):
        self.SPECIAL_BUTTONS = 5
        self.ADD = 0
        self.LEVEL_UP = 1
        self.LEVEL_DOWN = 2
        self.UP = 3
        self.DOWN = 4
        self.FIRST_LEVEL = 5
        self.LEVELS_PER_PAGE = 8
        self.LEVEL_BUTTON_SPACING = 60

        buttons = ButtonSet()
        buttons.add(small_button((SCREEN_WIDTH - 40, SCREEN_HEIGHT//2 - 10)))
        buttons.add(small_button((SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 + 55)))
        buttons.add(small_button((SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 + 85)))
        buttons.add(small_button((SCREEN_WIDTH // 2 - 10, 20)))
        buttons.add(small_button((SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40)))

        buttons.draw_plus(self.ADD)
        buttons.draw_arrow(self.UP, buttons.ARROW_UP)
        buttons.draw_arrow(self.DOWN, buttons.ARROW_DOWN)
        buttons.draw_arrow(self.LEVEL_UP, buttons.ARROW_UP)
        buttons.draw_arrow(self.LEVEL_DOWN, buttons.ARROW_DOWN)

        self.buttons = buttons

        self.page = 0
        self.last_page = (levels.count_levels() - 1) // self.LEVELS_PER_PAGE

        self.selected_level_button = -1

        self.level_clicked = -1
        self.switch_to_editor = False

    def update_frame(self):
        self.buttons.update()
        if events.mouse.released:
            if self.buttons.touch_mouse == self.ADD:
                levels.make_new_level()
                self.change_page(self.last_page)
                self.update_level_buttons()

            elif self.buttons.touch_mouse == self.UP:
                if self.page > 0:
                    self.change_page(self.page - 1)
                else:
                    self.change_page(self.last_page)

            elif self.buttons.touch_mouse == self.DOWN:
                if self.page < self.last_page:
                    self.change_page(self.page + 1)
                else:
                    self.change_page(0)

            elif self.buttons.touch_mouse == self.LEVEL_UP:
                self.move_up_selected()

            elif self.buttons.touch_mouse == self.LEVEL_DOWN:
                self.move_down_selected()

            elif self.buttons.touch_mouse >= self.FIRST_LEVEL:
                if self.buttons.touch_mouse == self.selected_level_button:
                    self.switch_to_editor = True
                    return
                else:
                    self.buttons.deselect(self.selected_level_button)
                    self.selected_level_button = self.buttons.touch_mouse
                    self.buttons.select(self.selected_level_button)

        self.buttons.draw(final_display)

    def change_page(self, page):
        """Switches the menu page to the specified page."""
        self.page = page

        first_button = self.page * self.LEVELS_PER_PAGE + self.SPECIAL_BUTTONS
        last_button = first_button + self.LEVELS_PER_PAGE - 1

        for button_id in range(self.FIRST_LEVEL, self.buttons.button_count):
            if first_button <= button_id <= last_button:
                self.buttons.show(button_id)
            else:
                self.buttons.hide(button_id)

    def level_on_current_page(self, level_num):
        """Returns whether a level at the index level_num is on the
        current page.
        """
        if level_num // self.LEVELS_PER_PAGE == self.page:
            return True
        else:
            return False

    def update_level_buttons(self):
        """Reloads all the level buttons, even those not on the current page."""
        while self.buttons.button_count > self.SPECIAL_BUTTONS:
            self.buttons.pop()

        level_count = levels.count_levels()
        if level_count == 0:
            self.last_page = 0
        else:
            self.last_page = (level_count - 1) // self.LEVELS_PER_PAGE

            file = open("levels.txt", 'r')
            level_array = file.read().split(levels.LEVEL_SEPARATOR)
            file.close()

            y = self.LEVEL_BUTTON_SPACING
            for level_num, level_string in enumerate(level_array):
                this_level = levels.string_to_level(level_string)

                new_button = level_button((20, y), this_level, level_num)
                if not self.level_on_current_page(level_num):
                    new_button.hidden = True
                self.buttons.add(new_button)

                y %= self.LEVEL_BUTTON_SPACING * self.LEVELS_PER_PAGE
                y += self.LEVEL_BUTTON_SPACING

    def selected_level(self):
        return self.selected_level_button - self.SPECIAL_BUTTONS

    def move_down_selected(self):
        """Moves a level down a level."""
        if self.selected_level_button != -1:
            level_num = self.selected_level()
            if level_num != levels.count_levels() - 1:
                levels.swap_levels(level_num, level_num + 1)

                self.selected_level_button += 1
                self.update_level_buttons()
                self.buttons.select(self.selected_level_button)

    def move_up_selected(self):
        """Moves a level up a level."""
        if self.selected_level_button != -1:
            level_num = self.selected_level()
            if level_num != 0:
                levels.swap_levels(level_num, level_num - 1)

                self.selected_level_button -= 1
                self.update_level_buttons()
                self.buttons.select(self.selected_level_button)


def draw_tile(surface, layer_num, tile_id, pixel_position):
    levels.draw_debug_tile(surface, layer_num, tile_id, pixel_position)


class UndoState:
    """Stores one undo step."""
    def __init__(self, change_grid):
        changes = []
        for layer in range(levels.LAYER_COUNT):
            for column in range(levels.WIDTH):
                for row in range(levels.HEIGHT):
                    change = change_grid[layer][column][row]
                    if change != -1:
                        changes.append((change, layer, column, row))
        self.changes = tuple(changes)

    def to_string(self):
        """Converts the undo into a printable string."""
        return repr(self.changes)


class Editor:
    TOOLBOX_TOP = SCREEN_HEIGHT - 80
    TOOLBOX_LEFT = 225
    TOOLBOX_TILE_WIDTH = constants.TILE_WIDTH + 5
    TOOLBOX_TILE_HEIGHT = constants.TILE_HEIGHT + 5
    SHELLS_TOP = 30
    SHELLS_SPACING = 30
    SHELLS_CENTER = SCREEN_WIDTH - 50

    def __init__(self):
        self.undos = []
        self.changed = False
        self.changes_grid = [[[-1] * levels.HEIGHT for _ in range(levels.WIDTH)]
                             for _ in range(levels.LAYER_COUNT)]

        self.selected_layer = levels.LAYER_BLOCKS

        self.level = None
        self.level_num = -1
        self.selected_tile = levels.EMPTY

        self.level_surface = graphics.new_surface(constants.SCREEN_SIZE)
        self.ui_surface = graphics.new_surface(SCREEN_SIZE)

        self.SAVE_AND_EXIT = 0
        self.ADD_SHELL = 1
        self.REMOVE_SHELL = 2
        self.FIRST_SHELL_BUTTON = 3

        buttons = ButtonSet()
        buttons.add(small_button((20, SCREEN_HEIGHT - 40)))
        buttons.add(small_button((SCREEN_WIDTH - 65, SCREEN_HEIGHT - 230)))
        buttons.add(small_button((SCREEN_WIDTH - 65, SCREEN_HEIGHT - 200)))

        buttons.draw_arrow(self.SAVE_AND_EXIT, buttons.ARROW_LEFT)
        buttons.draw_plus(self.ADD_SHELL)
        buttons.draw_minus(self.REMOVE_SHELL)

        self.buttons = buttons

        self.placing_start = False
        self.placing_end = False

        self.switch_to_menu = False

    def load_level(self, level_num):
        self.level_num = level_num
        self.level = levels.load_level(level_num)

        self.level_surface.fill(constants.TRANSPARENT)
        self.level.draw_debug(self.level_surface, (0, 0))

        self.update_shell_picker(self.ui_surface)

    def update(self):
        self.buttons.update()
        if events.keys.pressed:
            key = events.keys.pressed_key
            if key == pygame.K_z:
                self.undo()

            elif key == pygame.K_TAB or key == pygame.K_DOWN:
                if self.selected_layer == levels.LAYER_COUNT - 1:
                    self.change_layer(0)
                else:
                    self.change_layer(self.selected_layer + 1)

            elif key == pygame.K_UP:
                if self.selected_layer == 0:
                    self.change_layer(levels.LAYER_COUNT - 1)
                else:
                    self.change_layer(self.selected_layer - 1)

            else:
                key_name = pygame.key.name(key)

                if key_name.isnumeric():
                    number_pressed = int(key_name)
                    valid_tile_ids = levels.LAYER_ID_COUNTS[self.selected_layer]
                    if 1 <= number_pressed <= valid_tile_ids:
                        self.selected_tile = number_pressed

        if events.mouse.released:
            if self.changed:
                self.add_undo(self.changes_grid)
                self.reset_changes_grid()

            mouse_button = self.buttons.touch_mouse
            if mouse_button == self.SAVE_AND_EXIT:
                levels.save_level(self.level_num, self.level)
                self.switch_to_menu = True

                return

            elif mouse_button == self.ADD_SHELL:
                self.add_shell()
            elif mouse_button == self.REMOVE_SHELL:
                self.remove_shell()
            elif mouse_button >= self.FIRST_SHELL_BUTTON:
                shell_num = (mouse_button - self.FIRST_SHELL_BUTTON) // 2 + 1

                # checks if it's a left or right button
                if (mouse_button - self.FIRST_SHELL_BUTTON) % 2:
                    self.shell_left(shell_num)
                else:
                    self.shell_right(shell_num)

            if self.selected_single_place():
                if self.selected_tile == levels.BLOCKS_START:
                    self.change_start()

                elif self.selected_tile == levels.BLOCKS_END:
                    self.change_end()

        if events.mouse.held:
            if not self.selected_single_place():
                mouse_tile = levels.grid_tile_position(events.mouse.position)
                if mouse_tile != self.level.start_tile:
                    if mouse_tile != self.level.end_tile:
                        self.change_tile_at_mouse()

    def draw(self, surface):
        surface.blit(self.ui_surface, (0, 0))
        self.draw_toolbox_selection(surface)
        surface.blit(self.level_surface, (0, 0))
        self.draw_mouse_tile(surface)
        self.buttons.draw(surface)

    def selected_single_place(self):
        """Returns whether the current tile is a tile which is placed only
        once.  Currently only means the start tile and the end tile."""
        if self.selected_layer == levels.LAYER_BLOCKS:
            if self.selected_tile == levels.BLOCKS_START:
                return True
            if self.selected_tile == levels.BLOCKS_END:
                return True
        return False

    def change_start(self):
        mouse_tile = levels.grid_tile_position(events.mouse.position)
        if not mouse_tile:
            return

        old_start = self.level.start_tile
        rect = levels.tile_rect(levels.tile_pixel_position(old_start))
        pygame.draw.rect(self.level_surface, constants.TRANSPARENT, rect)

        self.level.start_tile = mouse_tile
        rect = levels.tile_rect(levels.tile_pixel_position(mouse_tile))
        pygame.draw.rect(self.level_surface, levels.DEBUG_START_COLOR, rect)

    def change_end(self):
        mouse_tile = levels.grid_tile_position(events.mouse.position)
        if not mouse_tile:
            return

        old_end = self.level.end_tile
        rect = levels.tile_rect(levels.tile_pixel_position(old_end))
        pygame.draw.rect(self.level_surface, constants.TRANSPARENT, rect)

        self.level.end_tile = mouse_tile
        rect = levels.tile_rect(levels.tile_pixel_position(mouse_tile))
        pygame.draw.rect(self.level_surface, levels.DEBUG_END_COLOR, rect)

    def change_layer(self, layer):
        """Changes the currently selected layer to the specified layer."""
        if layer < levels.LAYER_COUNT:
            self.selected_layer = layer
            self.selected_tile = levels.EMPTY

    def init_editor_ui(self):
        graphics.draw_tile_grid(self.ui_surface, (30, 30, 30))
        self.draw_toolbox(self.ui_surface)
        self.update_shell_picker(self.ui_surface)

    def draw_toolbox(self, surface):
        # draws tiles
        y = self.TOOLBOX_TOP
        for layer in range(levels.LAYER_COUNT):
            x = self.TOOLBOX_LEFT

            for tile in range(1, levels.LAYER_ID_COUNTS[layer] + 1):
                draw_tile(surface, layer, tile, (x, y))
                x += self.TOOLBOX_TILE_WIDTH

            y += self.TOOLBOX_TILE_HEIGHT

        # draws hotkey numbers
        x = self.TOOLBOX_LEFT + 6
        for tile in range(1, max(levels.LAYER_ID_COUNTS) + 1):
            number = TAHOMA.render(str(tile), False, constants.WHITE)
            surface.blit(number, (x, y))

            x += self.TOOLBOX_TILE_WIDTH

    def draw_toolbox_selection(self, surface):
        tile_width = self.TOOLBOX_TILE_WIDTH
        tile_height = self.TOOLBOX_TILE_HEIGHT
        layer = self.selected_layer

        layer_x = self.TOOLBOX_LEFT - 6
        layer_y = self.TOOLBOX_TOP - 6 + self.selected_layer * tile_height
        layer_w = levels.LAYER_ID_COUNTS[layer] * tile_width + 6
        layer_h = constants.TILE_HEIGHT + 11
        layer_rect = (layer_x, layer_y, layer_w, layer_h)
        pygame.draw.rect(surface, constants.MAGENTA, layer_rect, 2)

        tile_x = layer_x + 3 + (self.selected_tile - 1) * tile_width
        tile_y = layer_y + 3
        tile_w = constants.TILE_WIDTH + 5
        tile_h = constants.TILE_HEIGHT + 5
        tile_rect = (tile_x, tile_y, tile_w, tile_h)
        pygame.draw.rect(surface, constants.MAGENTA, tile_rect, 2)

    def add_shell(self):
        self.level.start_shells.insert(0, ball.NORMAL)
        self.update_shell_picker(self.ui_surface)

    def remove_shell(self):
        if len(self.level.start_shells) > 1:
            self.level.start_shells.pop(0)
            self.update_shell_picker(self.ui_surface)

    def shell_left(self, shell_num):
        index = len(self.level.start_shells) - 1 - shell_num
        if self.level.start_shells[index] == 1:
            self.level.start_shells[index] = ball.SHELL_TYPES
        else:
            self.level.start_shells[index] = self.level.start_shells[index] - 1
        self.update_shell_picker(self.ui_surface)

    def shell_right(self, shell_num):
        index = len(self.level.start_shells) - 1 - shell_num
        if self.level.start_shells[index] == ball.SHELL_TYPES:
            self.level.start_shells[index] = 1
        else:
            self.level.start_shells[index] = self.level.start_shells[index] + 1
        self.update_shell_picker(self.ui_surface)

    def update_shell_picker(self, surface):
        cover_rect = (SCREEN_WIDTH - 100, 0, 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(surface, constants.BLACK, cover_rect)

        self.buttons.slice_to(self.FIRST_SHELL_BUTTON)

        x = self.SHELLS_CENTER
        y = self.SHELLS_TOP
        radius = ball.SMALLEST_RADIUS

        color = ball.SHELL_DEBUG_COLORS[ball.CENTER]
        pygame.draw.circle(surface, color, (x, y), radius)
        y += self.SHELLS_SPACING
        radius += ball.SHELL_WIDTH

        for shell in reversed(self.level.start_shells[:-1]):
            color = ball.SHELL_DEBUG_COLORS[shell]
            pygame.draw.circle(surface, color, (x, y), radius, ball.SHELL_WIDTH)

            self.buttons.add(small_button((x - 45, y - 15)))
            self.buttons.draw_arrow(-1, self.buttons.ARROW_LEFT)
            self.buttons.add(small_button((x + 15, y - 15)))
            self.buttons.draw_arrow(-1, self.buttons.ARROW_RIGHT)

            y += self.SHELLS_SPACING
            radius += ball.SHELL_WIDTH

    def change_tile(self, tile_id, tile_position):
        """Changes the tile at tile_position to tile_id.

        tile_position is a (layer, column, row) triplet.
        """
        self.level.change_tile(tile_id, tile_position)
        self.level.draw_tile_at(self.level_surface, tile_position[1:])

    def draw_mouse_tile(self, surface):
        """Draws the tile that the mouse is holding, onto the editor grid."""
        mouse_position = events.mouse.position
        tile = self.selected_tile

        grid_position = levels.grid_pixel_position(mouse_position)
        if grid_position:
            draw_tile(surface, self.selected_layer, tile, grid_position)

    def change_tile_at_mouse(self):
        grid_position = levels.grid_tile_position(events.mouse.position)
        if grid_position:
            layer = self.selected_layer
            column, row = grid_position
            tile_position = (layer, column, row)

            if self.level.tile_at(tile_position) != self.selected_tile:
                # here we do all the things pertaining to undoing
                self.changed = True
                previous_tile = self.level.tile_at(tile_position)
                self.changes_grid[layer][column][row] = previous_tile

                # here we actually change the tile
                self.change_tile(self.selected_tile, tile_position)

    def reset_changes_grid(self):
        self.changed = False
        for layer in range(levels.LAYER_COUNT):
            for column in range(levels.WIDTH):
                for row in range(levels.HEIGHT):
                    self.changes_grid[layer][column][row] = -1

    def add_undo(self, changes_grid):
        self.undos.append(UndoState(changes_grid))

    def apply_undo(self, undo):
        for change in undo.changes:
            self.change_tile(change[0], (change[1], change[2], change[3]))

    def undo(self):
        if self.undos:
            self.apply_undo(self.undos[-1])
            self.undos.pop(-1)


MENU = 0
EDITOR = 1

main_menu = MainMenu()
main_menu.update_level_buttons()
main_menu.change_page(main_menu.last_page)

editor = Editor()

current_screen = MENU

while True:
    events.update()

    if current_screen == MENU:
        main_menu.update_frame()

        if main_menu.switch_to_editor:
            main_menu.switch_to_editor = False
            current_screen = EDITOR

            editor.load_level(main_menu.selected_level())
            editor.init_editor_ui()

            main_menu.selected_level_button = -1

    elif current_screen == EDITOR:
        editor.update()
        editor.draw(final_display)

        if editor.switch_to_menu:
            editor.undos = []
            editor.switch_to_menu = False
            current_screen = MENU
            main_menu.update_level_buttons()

    screen_update()
