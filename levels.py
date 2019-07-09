import pygame

import math
import geometry
import constants

pygame.init()

# Note that the levels in levels.txt are saved flipped along the bottom-left
# top-right diagonal - that is, each "row" in the file is actually a column
# in-game, and vice versa.  This is so that when retrieving things from the
# 2D matrix that represents the level, the x coordinate comes first and the
# y coordinate comes second.

WIDTH = constants.LEVEL_WIDTH
HEIGHT = constants.LEVEL_HEIGHT
PIXEL_WIDTH = WIDTH * constants.TILE_WIDTH
PIXEL_HEIGHT = HEIGHT * constants.TILE_HEIGHT

LAYER_ID_COUNTS = (8, 9)
EMPTY = 1
BLOCKS_WALL = 2
# The corner blocks are named based off of the two flat sides of the block.
# For example, on BLOCKS_TOPLEFT, the top and left sides are flat, and the
# diagonal is from the topright to the bottomleft.
BLOCKS_TOPLEFT = 3
BLOCKS_TOPRIGHT = 4
BLOCKS_BOTTOMRIGHT = 5
BLOCKS_BOTTOMLEFT = 6
BLOCKS_START = 7
BLOCKS_END = 8

BUTTONS_LEFT = 2
BUTTONS_UP = 3
BUTTONS_RIGHT = 4
BUTTONS_DOWN = 5
BUTTONS_TOPLEFT = 6
BUTTONS_TOPRIGHT = 7
BUTTONS_BOTTOMRIGHT = 8
BUTTONS_BOTTOMLEFT = 9


LAYER_COUNT = constants.LAYERS
LAYER_BLOCKS = constants.LAYER_BLOCKS
LAYER_BUTTONS = constants.LAYER_BUTTONS


DEBUG_START_COLOR = constants.YELLOW
DEBUG_END_COLOR = constants.MAGENTA


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


def swap_levels(level_num1, level_num2):
    """Swaps the position of two levels."""
    if level_num1 < 0 or level_num2 < 0:
        raise Exception("Attempted to swap level below 0!")

    file = open("levels.txt", 'r')
    level_array = file.read().split(LEVEL_SEPARATOR)
    file.close()

    level_count = len(level_array)
    if level_num1 >= level_count or level_num2 >= level_count:
        raise Exception("Attempted to swap level past last level!")

    temp = level_array[level_num1]
    level_array[level_num1] = level_array[level_num2]
    level_array[level_num2] = temp

    string = LEVEL_SEPARATOR.join(level_array)

    file = open("levels.txt", 'w')
    file.write(string)
    file.close()


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
    strings = string.split(LAYER_SEPARATOR)

    shell_strings = strings[0]
    shell_values = [int(shell) for shell in shell_strings.split()]

    start_end_string = strings[1]
    start_end_values = [int(value) for value in start_end_string.split()]

    layer_strings = strings[2:]
    layers = [string_to_layer(layer_string) for layer_string in layer_strings]

    new_level = Level()
    new_level.layers = layers
    new_level.start_tile = (start_end_values[0], start_end_values[1])
    new_level.end_tile = (start_end_values[2], start_end_values[3])
    new_level.start_shells = shell_values
    for column in range(WIDTH):
        for row in range(HEIGHT):
            if new_level.is_button((column, row)):
                new_level.total_buttons += 1

    return new_level


BUTTON_THICKNESS = 5


def draw_debug_tile(surface, layer_num, tile_id, pixel_position):
    tile_width = constants.TILE_WIDTH
    tile_height = constants.TILE_HEIGHT
    x, y = pixel_position

    if tile_id == EMPTY:
        rect = (x, y, tile_width, tile_height)
        pygame.draw.rect(surface, constants.TRANSPARENT, rect)
        return

    if layer_num == LAYER_BLOCKS:
        if tile_id == BLOCKS_WALL:
            rect = (x, y, tile_width, tile_height)
            pygame.draw.rect(surface, constants.WHITE, rect)

        elif tile_id == BLOCKS_START:
            rect = (x, y, tile_width, tile_height)
            pygame.draw.rect(surface, DEBUG_START_COLOR, rect)

        elif tile_id == BLOCKS_END:
            rect = (x, y, tile_width, tile_height)
            pygame.draw.rect(surface, DEBUG_END_COLOR, rect)

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
            # draws diagonal buttons
            # points start from topmost and travel clockwise
            width = constants.TILE_WIDTH
            height = constants.TILE_HEIGHT
            thickness = BUTTON_THICKNESS - 1
            points = [(0, 0) for _ in range(4)]
            if tile_id == BUTTONS_TOPLEFT:
                points[0] = (width - thickness, thickness)
                points[1] = (width, thickness * 2)
                points[2] = (thickness * 2, height)
                points[3] = (thickness, height - thickness)
            elif tile_id == BUTTONS_TOPRIGHT:
                points[0] = (thickness, thickness)
                points[1] = (width - thickness, height - thickness)
                points[2] = (width - thickness * 2, height)
                points[3] = (0, thickness * 2)
            elif tile_id == BUTTONS_BOTTOMRIGHT:
                points[0] = (width - thickness * 2, 0)
                points[1] = (width - thickness, thickness)
                points[2] = (thickness, height - thickness)
                points[3] = (0, height - thickness * 2)
            elif tile_id == BUTTONS_BOTTOMLEFT:
                points[0] = (thickness * 2, 0)
                points[1] = (width, height - thickness * 2)
                points[2] = (width - thickness, height - thickness)
                points[3] = (thickness, thickness)
            else:
                return

            for point in range(4):
                points[point] = (points[point][0] + x, points[point][1] + y)

            pygame.draw.polygon(surface, constants.RED, points)

            return

        pygame.draw.rect(surface, constants.RED, (x, y, width, height))


def grid_tile_position(point):
    """Returns the row and column of the tile that the given point is on."""
    column = int(point[0] // constants.TILE_WIDTH)
    row = int(point[1] // constants.TILE_HEIGHT)

    if not out_of_bounds((column, row)):
        return column, row
    else:
        return None


def grid_pixel_position(point):
    """Returns the top left corner of the tile that the point is on."""
    tile_position = grid_tile_position(point)

    if tile_position and not out_of_bounds(tile_position):
        x = tile_position[0] * constants.TILE_WIDTH
        y = tile_position[1] * constants.TILE_HEIGHT
        return x, y
    else:
        return None


def tile_pixel_position(tile_position):
    """Returns the top left corner of a given tile."""
    column, row = tile_position
    return column * constants.TILE_WIDTH, row * constants.TILE_HEIGHT


def tile_rect(pixel_position):
    """Returns a rectangle the size of a tile.

    pixel_position is the topleft of the tile."""
    width = constants.TILE_WIDTH
    height = constants.TILE_HEIGHT
    return pixel_position[0], pixel_position[1], width, height


def middle_pixel(tile_position):
    x = tile_position[0] * constants.TILE_WIDTH + constants.TILE_WIDTH // 2
    y = tile_position[1] * constants.TILE_HEIGHT + constants.TILE_HEIGHT // 2
    return x, y


BALL_CHECKS = 16


def tiles_touching_ball(radius, ball_center):
    """Returns a set of tuples, each a (column, row) pair, of the tiles
    that the ball touches.  Note that this is not necessarily 100%
    accurate, since it simply checks a few points around the circumference
    of the ball (the amount of points is defined by _BALL_CHECKS).
    """
    tile_list = []

    center_x, center_y = ball_center
    for point_num in range(BALL_CHECKS):
        angle = math.pi * 2.0 * (point_num / BALL_CHECKS)
        delta_x, delta_y = geometry.vector_to_difference(angle, radius - 1)

        point = (center_x + delta_x, center_y + delta_y)
        tile_list.append(grid_tile_position(point))

    return set(tile_list)


def is_ground(tile_type):
    if tile_type == BLOCKS_WALL:
        return True
    if tile_type == BLOCKS_TOPLEFT:
        return True
    if tile_type == BLOCKS_TOPRIGHT:
        return True
    return False


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
        start_x, start_y = position
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
        self.start_tile = (WIDTH // 2, HEIGHT // 2)
        self.end_tile = (WIDTH // 2 + 5, HEIGHT // 2)
        self.start_shells = [0]  # the shells that the ball starts with
        self.total_buttons = 0
        self.pressed_buttons = 0
        self.pressed_grid = [[False] * HEIGHT for _ in range(WIDTH)]

    def to_string(self):
        """Converts the level into a string, for writing to files."""
        shell_string = " ".join([str(shell) for shell in self.start_shells])
        start_string = str(self.start_tile[0]) + " " + str(self.start_tile[1])
        end_string = str(self.end_tile[0]) + " " + str(self.end_tile[1])
        layer_strings = [layer.to_string() for layer in self.layers]

        final_string = shell_string + LAYER_SEPARATOR
        final_string += start_string + " " + end_string + LAYER_SEPARATOR
        final_string += LAYER_SEPARATOR.join(layer_strings)
        return final_string

    def tile_at(self, tile_position):
        """Returns the tile type that is occupying a given position.

        tile_position is a (layer, column, row) triplet.
        """
        layer = self.layers[tile_position[0]]
        return layer.tile_at((tile_position[1], tile_position[2]))

    def draw_tile_at(self, surface, tile_position, grid_top_left=(0, 0)):
        """Draws the tiles (on all layers) occupying a given position.

        tile_position is a (column, row)
        """
        x_offset, y_offset = grid_top_left
        tile_pixel = tile_pixel_position(tile_position)
        pixel_position = (x_offset + tile_pixel[0], y_offset + tile_pixel[1])

        rect = tile_rect(pixel_position)
        pygame.draw.rect(surface, constants.TRANSPARENT, rect)

        for layer in range(LAYER_COUNT):
            tile = self.layers[layer].tile_at(tile_position)

            if tile != EMPTY:
                draw_debug_tile(surface, layer, tile, pixel_position)

    def draw_debug(self, surface, pixel_position):
        """Draws the level in a simplified manner, without sprites."""
        for column in range(WIDTH):
            for row in range(HEIGHT):
                self.draw_tile_at(surface, (column, row), pixel_position)

        self.draw_debug_start_end(surface, pixel_position)

    def draw_debug_layer(self, surface, layer, pixel_position):
        """Draws only one layer in the level, simplified, without sprites."""
        start_x, start_y = pixel_position

        if layer == LAYER_BLOCKS:
            for column in range(WIDTH):
                for row in range(HEIGHT):
                    if self.tile_at((LAYER_BLOCKS, column, row)) != EMPTY:
                        x = start_x + column * constants.TILE_WIDTH
                        y = start_y + row * constants.TILE_HEIGHT
                        tile = self.tile_at((layer, column, row))
                        draw_debug_tile(surface, layer, tile, (x, y))

        elif layer == LAYER_BUTTONS:
            for column in range(WIDTH):
                for row in range(HEIGHT):
                    if self.tile_at((LAYER_BUTTONS, column, row)) != EMPTY:
                        if not self.is_pressed((column, row)):
                            x = start_x + column * constants.TILE_WIDTH
                            y = start_y + row * constants.TILE_HEIGHT
                            tile = self.tile_at((layer, column, row))
                            draw_debug_tile(surface, layer, tile, (x, y))

    def draw_debug_start_end(self, surface, pixel_position):
        """Draws the start and end of the level, simplified, without sprites."""
        x, y = tile_pixel_position(self.start_tile)
        x += pixel_position[0]
        y += pixel_position[1]
        pygame.draw.rect(surface, DEBUG_START_COLOR, tile_rect((x, y)))

        x, y = tile_pixel_position(self.end_tile)
        x += pixel_position[0]
        y += pixel_position[1]
        pygame.draw.rect(surface, DEBUG_END_COLOR, tile_rect((x, y)))

    def change_tile(self, tile_id, tile_position):
        """Changes the tile at a certain position.

        tile_position is a (layer, column, row) triplet.
        """
        layer = self.layers[tile_position[0]]
        layer.change_tile(tile_id, (tile_position[1], tile_position[2]))

    def tile_to_segments(self, tile_position):
        """Returns a list of Segments representing a tile at the specified
        tile_position.  This will always only check LAYER_BLOCKS.

        tile_position is a (column, row pair).
        """
        layer = self.layers[LAYER_BLOCKS]
        tile = layer.tile_at(tile_position)

        if tile == EMPTY:
            return []

        else:
            width = constants.TILE_WIDTH
            height = constants.TILE_HEIGHT
            x = tile_position[0] * constants.TILE_WIDTH
            y = tile_position[1] * constants.TILE_HEIGHT
            top_left = (x, y)
            top_right = (x + width, y)
            bottom_right = (x + width, y + height)
            bottom_left = (x, y + height)

            if tile == BLOCKS_WALL:
                points = (top_left, top_right, bottom_right, bottom_left)
            elif tile == BLOCKS_TOPLEFT:
                points = (top_left, top_right, bottom_left)
            elif tile == BLOCKS_TOPRIGHT:
                points = (top_right, bottom_right, top_left)
            elif tile == BLOCKS_BOTTOMRIGHT:
                points = (bottom_right, bottom_left, top_right)
            elif tile == BLOCKS_BOTTOMLEFT:
                points = (bottom_left, top_left, bottom_right)
            else:
                return []

            return geometry.points_to_segment_list(points)

    def is_button(self, tile_position):
        """Returns whether a tile contains a button or not."""
        tile = self.layers[LAYER_BUTTONS].tile_at(tile_position)
        if tile == EMPTY:
            return False
        return True

    def unpress(self, tile_position):
        """Unpresses the button at the given position."""
        tile = self.layers[LAYER_BUTTONS].tile_at(tile_position)
        if tile == EMPTY:
            raise Exception("There is no button on tile " + str(tile_position))

        if self.is_pressed(tile_position):
            self.pressed_grid[tile_position[0]][tile_position[1]] = False
            self.pressed_buttons -= 1

    def press(self, tile_position):
        """Presses the button at a given position."""
        tile = self.layers[LAYER_BUTTONS].tile_at(tile_position)
        if tile == EMPTY:
            raise Exception("There is no button on tile " + str(tile_position))

        if not self.is_pressed(tile_position):
            self.pressed_grid[tile_position[0]][tile_position[1]] = True
            self.pressed_buttons += 1

    def is_pressed(self, tile_position):
        """Returns whether a tile is pressed or not.

        If no button exists on the tile, this returns False.
        """
        return self.pressed_grid[tile_position[0]][tile_position[1]]
