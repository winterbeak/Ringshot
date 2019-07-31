import pygame
import os
import random

import constants
import geometry


pygame.init()
pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


LEFT = 1
UP = 2
RIGHT = 3
DOWN = 4


def draw_arrow(surface, color, rect, direction, width=0):
    """Draws a triangle that fits into the rect, pointing in the given
    direction.
    """
    x, y, w, h = rect

    # points start from the tip of the arrow, and travel clockwise
    if direction == LEFT:
        points = ((x, y + h / 2), (x + w, y), (x + w, y + h))
    elif direction == UP:
        points = ((x + w / 2, y), (x + w, y + h), (x, y + h))
    elif direction == RIGHT:
        points = ((x + w, y + h / 2), (x, y + h), (x, y))
    elif direction == DOWN:
        points = ((x + w / 2, y + h), (x, y), (x + w, y))
    else:
        return

    pygame.draw.polygon(surface, color, points, width)


def screen_position(position):
    """All calculations are from (0, 0), while all drawing is done
    from SCREEN_TOP_LEFT.  This converts a calculated position to a drawable
    position.
    """
    x = position[0] + constants.SCREEN_LEFT
    y = position[1] + constants.SCREEN_TOP
    return int(x), int(y)


def new_surface(size):
    surface = pygame.Surface(size)
    surface.set_colorkey(constants.TRANSPARENT)
    surface.fill(constants.TRANSPARENT)
    return surface


def load_image(path, multiplier=1):
    image = pygame.image.load(os.path.join("images", path + ".png"))
    if multiplier > 1:
        width = image.get_width() * multiplier
        height = image.get_height() * multiplier
        image = pygame.transform.scale(image, (width, height))
    image.convert()
    image.set_colorkey(constants.TRANSPARENT)
    return image


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


class Shaker:
    """Shakes the screen.  This was way too inefficient and laggy, so
    I'm not actually going to use it.  Instead, I just manually adjust
    the position of everything I draw.
    """
    def __init__(self):
        self.temp_surface = new_surface(constants.FULL_SIZE)
        self.power = 0

    def shake(self, surface, background_color=constants.BLACK):
        if self.power == 0:
            return

        x = random.randint(-self.power, self.power)
        y = random.randint(-self.power, self.power)
        self.temp_surface.blit(surface, (0, 0))
        surface.fill(background_color)
        surface.blit(self.temp_surface, (x, y))

        self.power = 0

    def set_power(self, power):
        self.power = power


shaker = Shaker()


class Spritesheet:
    """Stores a spritesheet made of all of a thing's animations."""
    def __init__(self, sheet_path, frame_w, frame_h, frame_counts, multiplier=1):
        self.surface = load_image(sheet_path)
        self.full_w = self.surface.get_width() * multiplier
        self.full_h = self.surface.get_height() * multiplier
        if multiplier > 1:
            dimensions = self.full_w, self.full_h
            self.surface = pygame.transform.scale(self.surface, dimensions)
        self.surface.set_colorkey(constants.TRANSPARENT)

        self.frame_w = multiplier * frame_w
        self.frame_h = multiplier * frame_h
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


class Button:
    """Level Editor uses its own Button class - this one is going to be
    more generally applicable."""
    UNPRESSED = 0
    PRESSED = 1

    def __init__(self, position, sprite_sheet):
        self.sprite = SpriteInstance(sprite_sheet)
        self.pressed = False
        self.x = position[0]
        self.y = position[1]
        self.width = self.sprite.sheet.frame_w
        self.height = self.sprite.sheet.frame_h

    def draw(self, surface):
        surface.blit(self.sprite.get_now_frame(), (self.x, self.y))

    def touching_point(self, point):
        """Returns whether the button touches a given point or not."""
        if self.x <= point[0] <= self.x + self.width:
            if self.y <= point[1] <= self.y + self.height:
                return True
        return False

    def press(self):
        self.pressed = True
        self.sprite.current_anim = self.PRESSED

    def unpress(self):
        self.pressed = False
        self.sprite.current_anim = self.UNPRESSED


class CircleButton:
    def __init__(self, position, radius):
        self.x = int(position[0])
        self.y = int(position[1])
        self.radius = radius

    def touching_point(self, point):
        if geometry.distance((self.x, self.y), point) < self.radius:
            return True
        return False


ripples = []


class Ripple:
    def __init__(self, position, color, final_radius=20, expansion_rate=2.0):
        self.position = (int(position[0]), int(position[1]))
        self.radius = 1.0
        self.half_radius = final_radius // 2
        self.final_radius = final_radius
        self.width = 1.0

        self.expansion_rate = expansion_rate
        self.color = color
        self.done = False

    def update(self, slowmo=1.0):
        if self.radius <= self.half_radius:
            self.width += self.expansion_rate / 2 / slowmo
        elif self.radius >= self.final_radius:
            self.done = True
        else:
            self.width -= self.expansion_rate / 2 / slowmo
            if self.width < 1.0:
                self.width = 1.0

        self.radius += self.expansion_rate / slowmo

    def draw(self, surface, offset=(0, 0)):
        position = (self.position[0] + offset[0], self.position[1] + offset[1])
        radius = int(self.radius)
        width = int(self.width)
        pygame.draw.circle(surface, self.color, position, radius, width)


def create_ripple(position, color, final_radius=60, expansion_rate=2.0):
    ripples.append(Ripple(position, color, final_radius, expansion_rate))


def update_ripples(slowmo=1.0):
    ripple_num = len(ripples)
    for ripple in reversed(ripples):
        ripple_num -= 1
        ripple.update(slowmo)

        if ripple.done:
            del ripples[ripple_num]


def draw_ripples(surface, offset=(0, 0)):
    for ripple in ripples:
        ripple.draw(surface, offset)


def clear_ripples():
    ripples.clear()


def scale(surface, multiplier):
    width = int(surface.get_width() * multiplier)
    height = int(surface.get_height() * multiplier)
    return pygame.transform.scale(surface, (width, height))


font_numbers = load_image("numbers")
font_uppercase = load_image("uppercase")
font_lowercase = load_image("lowercase")
font_symbols = load_image("symbols")
valid_symbols = ('!', ',', '.', '?')  # in order of appearance in the image
valid_symbols_ascii = [ord(symbol) for symbol in valid_symbols]


def textify(string, multiplier=1):
    numbers = font_numbers
    uppercase = font_uppercase
    lowercase = font_lowercase
    symbols = font_symbols
    text_width = 9
    if multiplier != 1:
        numbers = scale(numbers, multiplier)
        uppercase = scale(uppercase, multiplier)
        lowercase = scale(lowercase, multiplier)
        symbols = scale(symbols, multiplier)
        text_width *= multiplier

    text_spacing = int(text_width + text_width / 9 * 2)

    text_surface = new_surface((len(string) * text_spacing, 21))
    for index, character in enumerate(string):
        position = (index * text_spacing, 0)

        ascii_value = ord(character)
        if 48 <= ascii_value <= 57:
            rect = ((ascii_value - 48) * text_width, 0, text_width, 15)
            text_surface.blit(numbers, position, rect)
        elif 65 <= ascii_value <= 90:
            rect = ((ascii_value - 65) * text_width, 0, text_width, 15)
            text_surface.blit(uppercase, position, rect)
        elif 97 <= ascii_value <= 122:
            rect = ((ascii_value - 97) * text_width, 0, text_width, 21)
            text_surface.blit(lowercase, position, rect)
        else:
            index = 0
            for symbol in valid_symbols_ascii:
                if symbol == ascii_value:
                    break
                index += 1
            else:
                continue

            rect = (index * text_width, 0, text_width, 21)
            text_surface.blit(symbols, position, rect)

    return text_surface
