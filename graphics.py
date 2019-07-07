import pygame
import os
import constants

pygame.init()


def new_surface(size):
    surface = pygame.Surface(size)
    surface.set_colorkey(constants.TRANSPARENT)
    surface.fill(constants.TRANSPARENT)
    return surface


def load_image(path):
    image = pygame.image.load(os.path.join("images", path))
    width = image.get_width() * constants.PIXEL
    height = image.get_height() * constants.PIXEL
    resized = pygame.transform.scale(image, (width, height))
    resized.convert()
    return resized


def border(surface, color, thickness):
    """Draws a border outlining the inside of a surface."""
    width = surface.get_width() - thickness * 2
    height = surface.get_height() - thickness * 2
    rect = (thickness, thickness, width, height)
    pygame.draw.rect(surface, color, rect, thickness)


def draw_grid(surface, color, columns, rows, cell_width, cell_height):
    for row in range(rows):
        start = (0, row * cell_height - 1)
        end = (columns * cell_width, row * cell_height - 1)
        pygame.draw.line(surface, color, start, end, 2)

    for column in range(columns):
        start = (column * cell_width - 1, 0)
        end = (column * cell_width - 1, rows * cell_height)
        pygame.draw.line(surface, color, start, end, 2)


def draw_tile_grid(surface, color):
    columns = constants.LEVEL_WIDTH
    rows = constants.LEVEL_HEIGHT
    width = constants.TILE_WIDTH
    height = constants.TILE_HEIGHT
    draw_grid(surface, color, columns, rows, width, height)


class Spritesheet:
    """Stores a spritesheet made of all of a thing's animations."""
    def __init__(self, sheet_path, frame_w, frame_h, frame_counts):
        self.surface = load_image(sheet_path)
        self.surface.set_colorkey(constants.TRANSPARENT)

        self.full_w = self.surface.get_width()
        self.full_h = self.surface.get_height()

        self.frame_w = constants.PIXEL*frame_w
        self.frame_h = constants.PIXEL*frame_h
        self.anim_count = int(self.full_w / frame_w)
        self.frame_counts = frame_counts
        self.z_height = 0

    def get_frame(self, anim_id, frame):
        """Returns a subsurface containing the specified frame of animation."""
        if anim_id >= self.anim_count:
            print("get_frame() tried to return a non-existant animation!")
        elif frame >= self.frame_counts[anim_id]:
            print("get_frame() tried to return a non-existant frame!")

        x = self.frame_w * anim_id
        y = self.frame_h * frame
        return self.surface.subsurface((x, y, self.frame_w, self.frame_h))


class SpriteInstance:
    def __init__(self, sheet):
        self.current_frame = 0
        self.current_anim = 0

        self.delay = 0

        self.sheet = sheet

    def set_frame(self, frame):
        self.current_frame = frame

    def get_now_frame(self):
        """Returns a subsurface containing the current frame."""
        return self.sheet.get_frame(self.current_anim, self.current_frame)

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame >= self.sheet.frame_counts[self.current_anim]:
            self.current_frame = 0

    def prev_frame(self):
        self.current_frame -= 1
        if self.current_frame <= -1:
            self.current_frame = self.sheet.frame_counts[self.current_anim] - 1

    def change_anim(self, anim_id):
        if anim_id >= self.sheet.anim_count:
            print("change_anim() tried to change to a nonexistant animation.")

        elif anim_id != self.current_anim:
            self.current_anim = anim_id
            self.current_frame = 0
            self.delay = 0

    def delay_next(self, delay):
        """delays flipping to the next animation frame for some frames

        note: must be called every frame of the delay"""
        if not self.delay:
            self.delay = delay
        else:
            self.delay -= 1

            if self.delay == 0:
                self.next_frame()
