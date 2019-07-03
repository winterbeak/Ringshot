import pygame

import constants

pygame.init()

# Note that the levels in levels.txt are saved flipped along the bottom-left
# top-right diagonal - that is, each "row" in the file is actually a column
# in-game, and vice versa.  This is so that when retrieving things from the
# 2D matrix that represents the level, the x coordinate comes first and the
# y coordinate comes second.

WIDTH = 25  # measured in tiles, not pixels
HEIGHT = 25
PIXEL_WIDTH = WIDTH * constants.TILE_WIDTH
PIXEL_HEIGHT = HEIGHT * constants.TILE_HEIGHT

LAYER_ID_COUNTS = (6, 5)
EMPTY = 1
BLOCKS_WALL = 2

# The corner blocks are named based off of which corner is "completely filled".
# For example, take this 3x3 representation of a TOPLEFT block:
#  ##/  The TOPLEFT corner is completely filled, the TOPRIGHT and BOTTOMLEFT
#  #/   corners are only half filled, and the BOTTOMRIGHT corner is not
#  /    filled at all.
BLOCKS_TOPLEFT = 3
BLOCKS_TOPRIGHT = 4
BLOCKS_BOTTOMRIGHT = 5
BLOCKS_BOTTOMLEFT = 6

BUTTONS_LEFT = 2
BUTTONS_UP = 3
BUTTONS_RIGHT = 4
BUTTONS_DOWN = 5


LAYER_COUNT = constants.LAYERS
LAYER_BLOCKS = constants.LAYER_BLOCKS
LAYER_BUTTONS = constants.LAYER_BUTTONS


# these are the characters that split up the different parts of levels.txt.
LEVEL_SEPARATOR = '*'    # character that separates each level
LAYER_SEPARATOR = '~'    # character that separates each layer in the level
COLUMN_SEPARATOR = '\n'  # character that separates each column in the level
TILE_SEPARATOR = ' '     # character that separates each tile in the column


def make_new_level():
    """Appends a new, completely empty level at the end of levels.txt."""
    if count_levels() == 0:  # There is no separator before the first level.
        string = ""
    else:
        string = LEVEL_SEPARATOR

    string += Level().to_string()

    file = open("levels.txt", 'a')
    file.write(string)
    file.close()


def save_level(level_num, updated_level):
    """Replaces the level at index level_num with updated_level.

    updated_level must be an instance of the Level class.
    """
    file = open("levels.txt", 'r')
    level_array = file.read().split(LEVEL_SEPARATOR)
    file.close()

    level_array[level_num] = updated_level.to_string()
    string = LEVEL_SEPARATOR.join(level_array)

    file = open("levels.txt", 'w')
    file.write(string)
    file.close()


def load_level(level_num):
    """Returns the level saved in levels.txt, at index level_num."""
    file = open("levels.txt", 'r')
    level_array = file.read().split(LEVEL_SEPARATOR)
    file.close()

    level = string_to_level(level_array[level_num])
    return level


def count_levels():
    """Returns the number of levels in the file."""
    file = open("levels.txt", 'r')
    file_string = file.read()
    file.close()

    if file_string == "" or file_string.isspace():
        return 0

    return file_string.count(LEVEL_SEPARATOR) + 1


def out_of_bounds(tile_position):
    """Returns whether a (column, row) pair is a valid coordinate inside
    the level.
    """
    if 0 <= tile_position[0] < WIDTH and 0 <= tile_position[1] < HEIGHT:
        return False
    return True


def string_to_layer(string):
    """Takes a string and converts it into a Layer object."""
    columns = string.split(COLUMN_SEPARATOR)

    string_grid = [column.split(TILE_SEPARATOR) for column in columns]
    grid = [[EMPTY] * HEIGHT for _ in range(WIDTH)]

    for column in range(WIDTH):
        for row in range(HEIGHT):
            grid[column][row] = int(string_grid[column][row])

    new_layer = Layer()
    new_layer.grid = grid
    return new_layer


def string_to_level(string):
    """Takes a string and converts it into a Level object."""
    layer_strings = string.split(LAYER_SEPARATOR)

    layers = [string_to_layer(layer_string) for layer_string in layer_strings]

    new_level = Level()
    new_level.layers = layers
    return new_level


BUTTON_THICKNESS = 5


def draw_debug_tile(surface, layer_num, tile_id, pixel_position):
    tile_width = constants.TILE_WIDTH
    tile_height = constants.TILE_HEIGHT
    x = pixel_position[0]
    y = pixel_position[1]

    if tile_id == EMPTY:
        rect = (x, y, tile_width, tile_height)
        pygame.draw.rect(surface, constants.TRANSPARENT, rect)
        return

    if layer_num == LAYER_BLOCKS:
        if tile_id == BLOCKS_WALL:
            rect = (x, y, tile_width, tile_height)
            pygame.draw.rect(surface, constants.WHITE, rect)

        else:
            top_left = (x, y)
            top_right = (x + tile_width - 1, y)
            bottom_right = (x + tile_width - 1, y + tile_height - 1)
            bottom_left = (x, y + tile_height - 1)

            if tile_id == BLOCKS_TOPLEFT:
                point_list = (top_left, top_right, bottom_left)
            elif tile_id == BLOCKS_TOPRIGHT:
                point_list = (top_left, top_right, bottom_right)
            elif tile_id == BLOCKS_BOTTOMRIGHT:
                point_list = (top_right, bottom_right, bottom_left)
            elif tile_id == BLOCKS_BOTTOMLEFT:
                point_list = (top_left, bottom_right, bottom_left)
            else:
                return

            pygame.draw.polygon(surface, constants.WHITE, point_list)

    elif layer_num == LAYER_BUTTONS:
        if tile_id == BUTTONS_LEFT:
            width = BUTTON_THICKNESS
            height = tile_height
        elif tile_id == BUTTONS_UP:
            width = tile_width
            height = BUTTON_THICKNESS
        elif tile_id == BUTTONS_RIGHT:
            x += tile_width - BUTTON_THICKNESS
            width = BUTTON_THICKNESS
            height = tile_height
        elif tile_id == BUTTONS_DOWN:
            y += tile_height - BUTTON_THICKNESS
            width = tile_width
            height = BUTTON_THICKNESS
        else:
            return
        pygame.draw.rect(surface, constants.RED, (x, y, width, height))


class Layer:
    def __init__(self):
        self.grid = [[EMPTY] * HEIGHT for _ in range(WIDTH)]

    def tile_at(self, tile_position):
        """Returns the tile at tile_position, which is a (column, row) pair."""
        if out_of_bounds(tile_position):
            return None
        return self.grid[tile_position[0]][tile_position[1]]

    def to_string(self):
        """Converts the layer into a string.  For writing to files."""
        column_strings = []
        for column in range(WIDTH):
            tile_strings = []

            for row in range(HEIGHT):
                tile_strings.append(str(self.grid[column][row]))

            column_strings.append(TILE_SEPARATOR.join(tile_strings))

        return COLUMN_SEPARATOR.join(column_strings)

    def draw_thumbnail(self, surface, position):
        """Draws a small thumbnail of the layer."""
        start_x = position[0]
        start_y = position[1]
        for column in range(WIDTH):
            for row in range(HEIGHT):
                if self.tile_at((column, row)) != EMPTY:
                    rect = (start_x + column * 2, start_y + row * 2, 2, 2)
                    surface.fill(constants.WHITE, rect)

    def change_tile(self, tile_id, tile_position):
        """Changes the tile at tile_position to tile_id.

        tile_position is a (column, row) pair.
        """
        self.grid[tile_position[0]][tile_position[1]] = tile_id


class Level:
    def __init__(self):
        self.layers = [Layer() for _ in range(LAYER_COUNT)]

    def to_string(self):
        """Converts the level into a string, for writing to files."""
        layer_strings = [layer.to_string() for layer in self.layers]

        final_string = LAYER_SEPARATOR.join(layer_strings)
        return final_string

    def tile_at(self, tile_position):
        """Returns the tile type that is occupying a given position.
        tile_position is a (layer, column, row) triplet."""
        layer = self.layers[tile_position[0]]
        return layer.tile_at((tile_position[1], tile_position[2]))

    def draw_debug(self, surface, pixel_position):
        """Draws the level in a simplified manner, without sprites."""
        start_x = pixel_position[0]
        start_y = pixel_position[1]

        for layer in reversed(range(LAYER_COUNT)):
            for column in range(WIDTH):
                for row in range(HEIGHT):
                    x = start_x + column * constants.TILE_WIDTH
                    y = start_y + row * constants.TILE_HEIGHT
                    tile = self.tile_at((layer, column, row))
                    draw_debug_tile(surface, layer, tile, (x, y))

    def draw_debug_layer(self, surface, layer, pixel_position):
        """Draws only one layer in the level, simplified, without sprites."""
        start_x = pixel_position[0]
        start_y = pixel_position[1]

        for column in range(WIDTH):
            for row in range(HEIGHT):
                x = start_x + column * constants.TILE_WIDTH
                y = start_y + row * constants.TILE_HEIGHT
                tile = self.tile_at((layer, column, row))
                draw_debug_tile(surface, layer, tile, (x, y))

    def change_tile(self, tile_id, tile_position):
        """Changes the tile at a certain position.

        tile_position is a (layer, column, row) triplet.
        """
        layer = self.layers[tile_position[0]]
        layer.change_tile(tile_id, (tile_position[1], tile_position[2]))
