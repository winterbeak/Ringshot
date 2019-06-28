import pygame

import constants

pygame.init()

WIDTH = 50  # measured in tiles, not pixels
HEIGHT = 50

BLOCK_TYPES = 2
EMPTY = 0
FULL_WALL = 1


def make_new_level():
    """Adds a new, completely empty level at the end of levels.txt."""
    file = open("levels.txt", 'a')
    string = "*" + Level().to_string()
    file.write(string)
    file.close()


def save_level(level_num, updated_level):
    """Replaces the level at index level_num with updated_level.

    updated_level must be an instance of the Level class.
    """
    file = open("levels.txt", 'r')
    level_array = file.read().split('*')
    level_array.pop(0)
    file.close()

    level_array[level_num] = updated_level.to_string()
    string = '*'.join(level_array)

    file = open("levels.txt", 'w')
    file.write(string)
    file.close()


def load_level(level_num):
    """Returns the Level at the index level_num."""
    file = open("levels.txt", 'r')
    level_array = file.read().split('*')
    level_array.pop(0)
    file.close()

    level = string_to_level(level_array[level_num])
    return level


def count_levels():
    """Returns the number of levels in the file."""
    file = open("levels.txt", 'r')
    return file.read().count('*')


def out_of_bounds(column, row):
    if 0 <= column < WIDTH and 0 <= row < HEIGHT:
        return False
    return True


def string_to_level(string):
    """Translates a string into a level grid, for reading from files."""
    rows = string.split("\n")
    grid_inverse = [row.split(" ") for row in rows]
    grid = [[0] * HEIGHT for _ in range(WIDTH)]

    for column in range(WIDTH):
        for row in range(HEIGHT):
            grid[column][row] = int(grid_inverse[row][column])

    new_level = Level()
    new_level.grid = grid
    return new_level


class Level:
    def __init__(self):
        self.grid = [[0] * WIDTH for _ in range(HEIGHT)]

    def tile_at(self, column, row):
        if out_of_bounds(column, row):
            return None
        return self.grid[column][row]

    def to_string(self):
        """Converts the level into a string, for writing to files."""
        string = ""
        for row in range(HEIGHT):
            for column in range(WIDTH):
                string += str(self.grid[column][row]) + " "

            string += "\n"

        return string

    def draw_thumbnail(self, surface, position):
        """Draws a small thumbnail of the level."""
        start_x = position[0]
        start_y = position[1]
        for row in range(HEIGHT):
            for column in range(WIDTH):
                if self.tile_at(column, row) != EMPTY:
                    rect = (start_x + column, start_y + row, 1, 1)
                    surface.fill(constants.WHITE, rect)

    def draw_debug(self, surface, position):
        """Draws the level using a single color and no sprites."""
        start_x = position[0]
        start_y = position[1]
        for row in range(HEIGHT):
            for column in range(WIDTH):
                if self.tile_at(column, row) == FULL_WALL:
                    x = start_x + column * constants.TILE_WIDTH
                    y = start_y + row * constants.TILE_HEIGHT
                    rect = (x, y, constants.TILE_WIDTH, constants.TILE_HEIGHT)
                    pygame.draw.rect(surface, constants.WHITE, rect)
