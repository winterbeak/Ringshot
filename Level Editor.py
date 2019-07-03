import pygame

import graphics
import levels
import constants
import events
# import debug


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

    def touches_point(self, point):
        if self.rect.collidepoint(point[0], point[1]):
            return True
        return False

    def draw(self, surface):
        if not self.hidden:
            if self.highlight:
                pygame.draw.rect(surface, self.HIGHLIGHT_COLOR, self.rect)
            surface.blit(self.sprite, (self.x, self.y))


class ButtonSet:
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
            else:
                button.highlight = False

        if not touching_a_button:
            self.touch_mouse = -1

    def add(self, button):
        self.buttons.append(button)
        self.button_count += 1

    def pop(self):
        self.buttons.pop()
        self.button_count -= 1

    def show(self, button_id):
        self.buttons[button_id].hidden = False

    def hide(self, button_id):
        self.buttons[button_id].hidden = True


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
        self.SPECIAL_BUTTONS = 3
        self.ADD = 0
        self.UP = 1
        self.DOWN = 2
        self.FIRST_LEVEL = 3
        self.LEVELS_PER_PAGE = 8
        self.LEVEL_BUTTON_SPACING = 60

        buttons = ButtonSet()
        buttons.add(small_button((SCREEN_WIDTH - 40, SCREEN_HEIGHT//2 - 10)))
        buttons.add(small_button((SCREEN_WIDTH // 2 - 10, 20)))
        buttons.add(small_button((SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40)))
        self.buttons = buttons

        self.page = 0
        self.last_page = (levels.count_levels() - 1) // self.LEVELS_PER_PAGE

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

            elif self.buttons.touch_mouse >= self.FIRST_LEVEL:
                self.switch_to_editor = True
                self.level_clicked = self.buttons.touch_mouse
                return

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


def grid_tile_position(point):
    """Returns the row and column of the tile that the given point is on."""
    column = point[0] // constants.TILE_WIDTH
    row = point[1] // constants.TILE_HEIGHT

    if not levels.out_of_bounds((column, row)):
        return column, row
    else:
        return None


def grid_pixel_position(point):
    """Returns the top left corner of the tile that the point is on."""
    tile_position = grid_tile_position(point)

    if tile_position and not levels.out_of_bounds(tile_position):
        x = tile_position[0] * constants.TILE_WIDTH
        y = tile_position[1] * constants.TILE_HEIGHT
        return x, y
    else:
        return None


def draw_tile(surface, layer_num, tile_id, tile_position):
    levels.draw_debug_tile(surface, layer_num, tile_id, tile_position)


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
    def __init__(self):
        self.undos = []
        self.changed = False
        self.changes_grid = [[[-1] * levels.HEIGHT for _ in range(levels.WIDTH)]
                             for _ in range(levels.LAYER_COUNT)]

        self.layer_num = levels.LAYER_BLOCKS

        self.level = None
        self.level_num = -1
        self.holding_tile = levels.EMPTY
        self.level_surface = graphics.new_surface(constants.SCREEN_SIZE)
        self.grid_surface = graphics.new_surface(constants.SCREEN_SIZE)
        color = (30, 30, 30)
        for row in range(levels.HEIGHT):
            start = (0, row * constants.TILE_HEIGHT - 1)
            end = (levels.PIXEL_WIDTH, row * constants.TILE_HEIGHT - 1)
            pygame.draw.line(self.grid_surface, color, start, end, 2)

        for column in range(levels.WIDTH):
            start = (column * constants.TILE_WIDTH - 1, 0)
            end = (column * constants.TILE_WIDTH - 1, levels.PIXEL_HEIGHT)
            pygame.draw.line(self.grid_surface, color, start, end, 2)

        self.SAVE_AND_EXIT = 0
        self.buttons = ButtonSet()
        self.buttons.add(small_button((20, SCREEN_HEIGHT - 40)))

        self.switch_to_menu = False

    def update_frame(self):
        self.buttons.update()
        if events.keys.pressed:
            if events.keys.pressed_key == pygame.K_z:
                self.undo()
            else:
                key_name = pygame.key.name(events.keys.pressed_key)

                if key_name.isnumeric():
                    number_pressed = int(key_name)
                    valid_tile_ids = levels.LAYER_ID_COUNTS[self.layer_num]
                    if 1 <= number_pressed <= valid_tile_ids:
                        self.holding_tile = number_pressed

        if events.mouse.released:
            if self.changed:
                self.add_undo(self.changes_grid)
                self.reset_changes_grid()

            if self.buttons.touch_mouse == self.SAVE_AND_EXIT:
                levels.save_level(self.level_num, self.level)
                self.switch_to_menu = True
                return

        if events.mouse.held:
            self.change_tile_at_mouse()

        final_display.blit(self.grid_surface, (0, 0))
        final_display.blit(self.level_surface, (0, 0))
        self.draw_mouse_tile(final_display)
        self.buttons.draw(final_display)

    def change_tile(self, tile_id, tile_position):
        """Changes the tile at tile_position to tile_id.

        tile_position is a (layer, column, row) triplet.
        """
        self.level.change_tile(tile_id, tile_position)

        x = tile_position[1] * constants.TILE_WIDTH
        y = tile_position[2] * constants.TILE_HEIGHT
        draw_tile(self.level_surface, tile_position[0], tile_id, (x, y))

    def draw_mouse_tile(self, surface):
        """Draws the tile that the mouse is holding, onto the editor grid."""
        mouse_position = events.mouse.position
        tile = self.holding_tile

        grid_position = grid_pixel_position(mouse_position)
        if grid_position:
            draw_tile(surface, self.layer_num, tile, grid_position)

    def change_tile_at_mouse(self):
        grid_position = grid_tile_position(events.mouse.position)
        if grid_position:
            layer = self.layer_num
            column = grid_position[0]
            row = grid_position[1]
            tile_position = (layer, column, row)

            if self.level.tile_at(tile_position) != self.holding_tile:
                # here we do all the things pertaining to undoing
                self.changed = True
                previous_tile = self.level.tile_at(tile_position)
                self.changes_grid[layer][column][row] = previous_tile

                # here we actually change the tile
                self.change_tile(self.holding_tile, tile_position)

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
            editor.level_num = main_menu.level_clicked - 3
            editor.level = levels.load_level(editor.level_num)

            editor.level_surface.fill(constants.TRANSPARENT)
            editor.level.draw_debug(editor.level_surface, (0, 0))

    elif current_screen == EDITOR:
        editor.update_frame()

        if editor.switch_to_menu:
            editor.undos = []
            editor.switch_to_menu = False
            current_screen = MENU
            main_menu.update_level_buttons()

    screen_update()
