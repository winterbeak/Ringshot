import sound

import pygame
import math
import random
import copy
import os

import constants
import events
import graphics
import geometry
import debug

import ball
import levels
import editor


def screen_update(fps):
    pygame.display.flip()
    final_display.fill(constants.BLACK)
    clock.tick(fps)


os.environ["SDL_VIDEO_CENTERED"] = "1"

# leave some pixels as a border, so it's less likely to click off the window
FULL_WIDTH = constants.FULL_WIDTH
FULL_HEIGHT = constants.FULL_HEIGHT
FULL_SIZE = constants.FULL_SIZE

SCREEN_LEFT = constants.SCREEN_LEFT
SCREEN_TOP = constants.SCREEN_TOP
TOP_LEFT = constants.SCREEN_TOP_LEFT

SCREEN_WIDTH = constants.SCREEN_WIDTH
SCREEN_HEIGHT = constants.SCREEN_HEIGHT

pygame.init()
pygame.display.set_caption("Ringshot")
final_display = pygame.display.set_mode(FULL_SIZE)

clock = pygame.time.Clock()

mouse_held = False
mouse_click = False
mouse_release = False

sound_transition = sound.load("transition")

LAST_LEVEL = 53

save_data = open("Easily Editable Save Data.txt", 'r')
last_unlocked = int(save_data.read())
save_data.close()

LEVELS_PER_COURSE = 18

logo_name = graphics.load_image("name", 4)
logo_bird_sprite = graphics.Spritesheet("logo", 10, 10, (11,), 4)
logo_bird = graphics.SpriteInstance(logo_bird_sprite)

logo_name_small = graphics.load_image("name_outlined", 2)
logo_bird_sprite_small = graphics.Spritesheet("logo_outlined", 10, 10, (11,), 2)
logo_bird_small = graphics.SpriteInstance(logo_bird_sprite_small)

game_title = graphics.load_image("title")
game_title_x = constants.SCREEN_MIDDLE[0] - game_title.get_width() // 2
game_title_y = constants.SCREEN_MIDDLE[1] - game_title.get_height() // 2 - 10

intro_text = graphics.textify("Click to start!", True)
intro_text_x = constants.SCREEN_MIDDLE[0] - intro_text.get_width() // 2 + 1
intro_text_y = constants.SCREEN_MIDDLE[1] + 25

menu_temp_surface = graphics.new_surface(constants.SCREEN_SIZE)


def render_level_number(number):
    return graphics.textify(str(number))


class MenuScreen:
    PAUSE_LENGTH = 60
    GROW_LENGTH = 120
    FADE_LENGTH = 60

    PAUSE_LAST = PAUSE_LENGTH
    GROW_LAST = PAUSE_LAST + GROW_LENGTH
    FADE_LAST = GROW_LAST + GROW_LENGTH

    CREDITS = 0
    LEVEL_SELECT = 1
    LEVEL_EDITOR = 2

    ARROW_WIDTH = 20
    ARROW_HEIGHT = 60
    LEFT_ARROW_X = 20
    RIGHT_ARROW_X = constants.FULL_WIDTH - 20 - ARROW_WIDTH
    ARROW_Y = constants.FULL_MIDDLE_INT[1] - ARROW_HEIGHT // 2

    PAGE_CHANGE_LENGTH = 30
    PAGE_CHANGE_A = -constants.FULL_WIDTH / (PAGE_CHANGE_LENGTH ** 2)

    LEFT = 1
    RIGHT = 2

    LOGO_WIDTH = 284
    LOGO_HEIGHT = 52
    LOGO_BIRD_X = (FULL_WIDTH - LOGO_WIDTH) // 2
    LOGO_BIRD_Y = FULL_HEIGHT - 100
    LOGO_NAME_X = LOGO_BIRD_X + 64
    LOGO_NAME_Y = LOGO_BIRD_Y - 12

    ZOOMED = 1
    ZOOMING_OUT = 2
    NORMAL = 3
    ZOOM_LENGTH = 30
    ZOOM_INITIAL = 2.6
    ZOOM_A = ZOOM_INITIAL - 1.0
    ZOOM_A /= ZOOM_LENGTH ** 2

    EDITOR_WIDTH = 400
    EDITOR_HEIGHT = 400
    EDITOR_LEVELS_IN_ROW = 9
    EDITOR_LEVELS_IN_COLUMN = 9
    EDITOR_HORIZONTAL_SPACING = EDITOR_WIDTH // (EDITOR_LEVELS_IN_ROW - 1)
    EDITOR_VERTICAL_SPACING = EDITOR_HEIGHT // (EDITOR_LEVELS_IN_COLUMN - 1)
    EDITOR_LEFT = (FULL_WIDTH - EDITOR_WIDTH) // 2
    EDITOR_TOP = (FULL_HEIGHT - EDITOR_HEIGHT) // 2

    EDITOR_THUMBNAIL_X = SCREEN_LEFT + 170
    EDITOR_THUMBNAIL_Y = SCREEN_TOP + SCREEN_HEIGHT - 190

    PLAY = 1
    EDIT = 2
    DELETE = 3
    LEVEL_LEFT = 4
    LEVEL_RIGHT = 5

    ADD = 6
    ADD_TEXT = graphics.textify("Add")
    ADD_WIDTH = ADD_TEXT.get_width()
    ADD_HEIGHT = ADD_TEXT.get_height()

    EDITOR_TEXTS = (graphics.textify("Play"), graphics.textify("Edit"),
                    graphics.textify("Delete"), graphics.textify("Move Left"),
                    graphics.textify("Move Right"))
    EDITOR_TEXTS_X = (EDITOR_THUMBNAIL_X + 100, EDITOR_THUMBNAIL_X + 100,
                      EDITOR_THUMBNAIL_X + 90, EDITOR_THUMBNAIL_X - 38,
                      EDITOR_THUMBNAIL_X + 78)
    EDITOR_TEXTS_Y = (EDITOR_THUMBNAIL_Y, EDITOR_THUMBNAIL_Y + 31,
                      EDITOR_THUMBNAIL_Y + 62, EDITOR_THUMBNAIL_Y - 31,
                      EDITOR_THUMBNAIL_Y - 31)
    EDITOR_TEXTS_BOXES = []
    for text in range(len(EDITOR_TEXTS)):
        EDITOR_TEXTS_BOXES.append(pygame.Rect(EDITOR_TEXTS_X[text],
                                              EDITOR_TEXTS_Y[text],
                                              EDITOR_TEXTS[text].get_width(),
                                              EDITOR_TEXTS[text].get_height()))

    EDITOR_NOTE_STRINGS = ("To load other's levels, simply",
                           "replace your levels.txt with theirs.",
                           "Note that this will overwrite",
                           "all your current levels.")
    EDITOR_NOTE_TEXT = graphics.text_wall(EDITOR_NOTE_STRINGS)
    EDITOR_NOTE_X = SCREEN_LEFT
    EDITOR_NOTE_X += (SCREEN_WIDTH - EDITOR_NOTE_TEXT.get_width()) // 2
    EDITOR_NOTE_Y = EDITOR_THUMBNAIL_Y + 100

    CREDITS_STRINGS = ("Made entirely with Python and Pygame",
                       "in about a month's time.",
                       "",
                       "Source code can be found at",
                       "github.com/snowdozer/ringshot.",
                       "",
                       "Font made by me.",
                       "",
                       "All sounds created with Ableton Live",
                       "Lite 9's royalty free libraries.",
                       "",
                       "Shoutouts to Mystery Tournament 14,",
                       "and also to my friends for testing this.")

    CREDITS_SUBTITLE = graphics.load_image("credits_subtitle")

    CREDITS_TEXT = graphics.text_wall(CREDITS_STRINGS)
    CREDITS_X = (FULL_WIDTH - CREDITS_TEXT.get_width()) // 2
    CREDITS_Y = FULL_HEIGHT // 2 - 10

    CREDITS_SUBTITLE_X = (FULL_WIDTH - CREDITS_SUBTITLE.get_width()) // 2
    CREDITS_SUBTITLE_Y = CREDITS_Y - 70

    def __init__(self):
        self.arrow_y_offset = 0.0
        self.arrow_frame = 0
        self.arrow_alpha = 0
        self.show_arrows = False

        self.page = self.LEVEL_SELECT
        self.next_page = 0
        self.changing_page = False
        self.page_frame = 0
        self.page_direction = 0
        self.x_offset = 0.0

        self.switch_to_level = False
        self.selected_level = -1
        self.transition_ball = None

        self.CIRCLE_RADII = (100, 140, 180, 220, 260)
        self.BUTTON_RING_RADII = (120, 160, 200, 240)
        self.angle_offsets = [0.6, 0.4, 0.2, 0.0]
        self.ROTATE_SPEED = 0.0005
        self.SHELL_COLORS = ball.SHELL_DEBUG_COLORS

        self.BUTTON_RADIUS = 16

        self.mouse_level = -1
        self.previous_frame_mouse_level = -1
        self.mouse_arrow = 0
        self.block_layers = levels.load_all_block_layers()

        self.grow_frame = 0
        self.grow_course = False
        self.grow_radius = 0.0
        self.target_radius = 0.0
        self.grow_a = 0.0
        self.level_alpha = 0

        self.zoom_state = self.NORMAL
        self.zoom_frame = 0
        self.zoom_amount = self.ZOOM_INITIAL
        self.unzoomed_surface = graphics.new_surface(constants.SCREEN_SIZE)
        self.first_zoom = True

        self.show_credits = False
        self.disable_clicking = False

        self.exit_fading = True
        self.exit_fade_delay = 0

        self.volume_text = graphics.textify("Volume")

        self.switch_to_editor = False
        self.last_editor_level = levels.count_levels()

        self.add_x = 0.0
        self.add_y = 0.0
        self.add_rect = None
        self.editor_left_x = 0.0
        self.editor_left_y = 0.0
        self.editor_left_rect = None
        self.editor_right_x = 0.0
        self.editor_right_y = 0.0
        self.editor_right_rect = None
        self.previous_frame_editor_button = 0
        self.update_add_level()

        self.editor_button = 0

        self.editor_note_cover = pygame.Surface(self.EDITOR_NOTE_TEXT.get_size())
        self.editor_note_cover.fill(constants.BLACK)
        self.in_transition = False

    def update(self):
        if self.exit_fading and graphics.fader.alpha == 0:
            if self.exit_fade_delay == 30:
                events.quit_program()

            self.exit_fade_delay += 1

        if events.keys.pressed_key == pygame.K_ESCAPE:
            if not self.disable_clicking:
                graphics.fader.fade_to(0)
                sound.volume_control.fade_to(0.0)

        self.update_menu_buttons()
        if self.page == self.LEVEL_EDITOR and not self.disable_clicking:
            self.editor_button = self.detect_editor_mouse_button()

        for angle_num in range(len(self.angle_offsets)):
            self.angle_offsets[angle_num] += self.ROTATE_SPEED
            self.angle_offsets[angle_num] %= math.pi * 2

        if self.grow_course:
            if self.grow_frame <= self.PAUSE_LAST:
                pass
            elif self.grow_frame <= self.GROW_LAST:
                a = self.grow_a
                x = self.grow_frame
                d = self.GROW_LAST
                c = self.target_radius
                self.grow_radius = a * (x - d) ** 2 + c
            elif self.level_alpha < 255:
                self.level_alpha += 10
                if self.level_alpha > 255:
                    self.level_alpha = 255
            else:
                self.grow_course = False
            self.grow_frame += 1

            return

        if self.zoom_state != self.NORMAL:
            if self.zoom_state == self.ZOOMED and events.mouse.released:
                self.zoom_state = self.ZOOMING_OUT
            if self.zoom_state == self.ZOOMING_OUT:
                if self.zoom_frame <= self.ZOOM_LENGTH:
                    self.zoom_amount = (self.zoom_frame - self.ZOOM_LENGTH) ** 2
                    self.zoom_amount = self.ZOOM_A * self.zoom_amount + 1.0
                    self.zoom_frame += 1
                else:
                    self.zoom_frame = 0
                    self.zoom_amount = 1.0
                    self.zoom_state = self.NORMAL
                    self.first_zoom = False
                    self.show_arrows = True
            return

        if not self.changing_page:
            if self.page == self.LEVEL_SELECT:
                mouse_level = self.touching_level(events.mouse.position)
                if mouse_level < last_unlocked:
                    self.mouse_level = mouse_level

                    if mouse_level != -1 and not self.disable_clicking:
                        if self.previous_frame_mouse_level != mouse_level:
                            course = self.mouse_level // LEVELS_PER_COURSE
                            if course == 0:
                                sound.normal_scale.play_random()
                            elif course == 1:
                                sound.ghost_scale.play_random()
                            elif course == 2:
                                sound.float_scale.play_random()

            elif self.page == self.LEVEL_EDITOR:
                mouse_level = self.touching_editor_level(events.mouse.position)

                if LAST_LEVEL < mouse_level < self.last_editor_level:
                    self.mouse_level = mouse_level

                    if mouse_level != -1 and not self.disable_clicking:
                        if self.previous_frame_mouse_level != mouse_level:
                            sound.normal_scale.play_random()
                else:
                    self.mouse_level = -1

                if self.editor_button != 0 and not self.disable_clicking:
                    if self.previous_frame_editor_button != self.editor_button:
                        sound.normal_scale.play_random()

        else:
            self.mouse_level = -1

        if events.mouse.released and not self.disable_clicking:
            if self.mouse_level != -1 and self.mouse_level < last_unlocked:
                self.selected_level = self.mouse_level
                self.switch_to_level = True

            elif 0 <= self.mouse_level < self.last_editor_level:
                self.selected_level = self.mouse_level

            elif self.mouse_arrow != 0:
                self.selected_level = -1

                self.show_arrows = False
                self.changing_page = True
                self.page_frame = 0

                if self.mouse_arrow == self.LEFT:
                    self.next_page = self.page - 1
                    self.page_direction = self.LEFT

                elif self.mouse_arrow == self.RIGHT:
                    self.next_page = self.page + 1
                    self.page_direction = self.RIGHT

            elif self.editor_button == self.PLAY:
                self.switch_to_level = True

            elif self.editor_button == self.EDIT:
                self.switch_to_editor = True

            elif self.editor_button == self.DELETE:
                levels.delete_level(self.selected_level)
                del self.block_layers[self.selected_level]
                if self.selected_level == self.last_editor_level - 1:
                    self.selected_level = -1

                self.last_editor_level -= 1
                self.update_add_level()

            elif self.editor_button == self.ADD:
                levels.make_new_level(self.last_editor_level)
                self.block_layers.append(levels.Layer())
                self.last_editor_level += 1
                self.update_add_level()

            elif self.editor_button == self.LEVEL_LEFT:
                if self.selected_level > LAST_LEVEL + 1:
                    level = self.selected_level
                    levels.swap_levels(level, level - 1)
                    temp = self.block_layers[level]
                    self.block_layers[level] = self.block_layers[level - 1]
                    self.block_layers[level - 1] = temp

                    self.selected_level -= 1

            elif self.editor_button == self.LEVEL_RIGHT:
                if self.selected_level < self.last_editor_level - 1:
                    level = self.selected_level
                    levels.swap_levels(level, level + 1)
                    temp = self.block_layers[level]
                    self.block_layers[level] = self.block_layers[level + 1]
                    self.block_layers[level + 1] = temp

                    self.selected_level += 1

        if self.changing_page:
            if self.page_frame < self.PAGE_CHANGE_LENGTH:
                self.x_offset = (self.page_frame - self.PAGE_CHANGE_LENGTH) ** 2
                self.x_offset = self.PAGE_CHANGE_A * self.x_offset
                if self.page_direction == self.RIGHT:
                    self.x_offset = -self.x_offset

                self.page_frame += 1
            else:
                self.changing_page = False
                self.page = self.next_page
                self.show_arrows = True

        self.previous_frame_editor_button = self.editor_button
        self.previous_frame_mouse_level = self.mouse_level
        logo_bird.delay_next(10)

    def draw(self, surface, position=(0, 0)):
        """Set level_hover to false if you don't want to draw the level
        being hovered over.
        """
        # Arrows
        if self.arrow_alpha != 0:
            y = self.ARROW_Y + self.arrow_y_offset + position[1]
            w = self.ARROW_WIDTH
            h = self.ARROW_HEIGHT
            color = (self.arrow_alpha, ) * 3
            if self.page != 0:
                x = self.LEFT_ARROW_X + position[0]
                direction = graphics.LEFT

                graphics.draw_arrow(surface, color, (x, y, w, h), direction)

            if self.page != 2:
                x = self.RIGHT_ARROW_X + position[0]
                direction = graphics.RIGHT

                graphics.draw_arrow(surface, color, (x, y, w, h), direction)

        if self.PAUSE_LAST < self.grow_frame <= self.GROW_LAST:
            shake_x = random.randint(-2, 2) + position[0]
            shake_y = random.randint(-2, 2) + position[1]
            self.draw_level_select(surface, shake_x, shake_y)

        elif self.changing_page:
            # Level select page
            if self.page == self.LEVEL_SELECT:
                if self.page_direction == self.LEFT:
                    x = self.x_offset + FULL_WIDTH + position[0]
                else:
                    x = self.x_offset - FULL_WIDTH + position[0]
                self.draw_level_select(surface, int(x))

            elif self.next_page == self.LEVEL_SELECT:
                x = self.x_offset + position[0]
                self.draw_level_select(surface, int(x))

            # Credits page
            if self.page == self.CREDITS:
                x = self.x_offset - FULL_WIDTH + position[0]
                self.draw_credits_options(surface, int(x))

            elif self.next_page == self.CREDITS:
                x = self.x_offset + position[0]
                self.draw_credits_options(surface, int(x))

            if self.page == self.LEVEL_EDITOR:
                x = self.x_offset + FULL_WIDTH + position[0]
                self.draw_editor(surface, int(x))
            elif self.next_page == self.LEVEL_EDITOR:
                x = self.x_offset + position[0]
                self.draw_editor(surface, int(x))

        elif self.page == self.LEVEL_SELECT:
            self.draw_level_select(surface, position[0], position[1])
        elif self.page == self.CREDITS:
            self.draw_credits_options(surface, position[0], position[1])
        elif self.page == self.LEVEL_EDITOR:
            self.draw_editor(surface, position[0], position[1])

    def draw_zoomed(self, surface, position=(0, 0)):
        position = (position[0] - SCREEN_LEFT, position[1] - SCREEN_TOP)
        self.unzoomed_surface.fill(constants.BLACK)
        self.draw(self.unzoomed_surface, position)

        y = intro_text_y + self.arrow_y_offset
        self.unzoomed_surface.blit(intro_text, (intro_text_x, y))
        self.unzoomed_surface.blit(game_title, (game_title_x, game_title_y))

        w = int(SCREEN_WIDTH * self.zoom_amount)
        h = int(SCREEN_HEIGHT * self.zoom_amount)
        x = int((FULL_WIDTH / 2) - (w / 2))
        y = int((FULL_HEIGHT / 2) - (h / 2))
        scaled_surface = pygame.transform.scale(self.unzoomed_surface, (w, h))
        surface.blit(scaled_surface, (x, y))

    def draw_level_select(self, surface, x_offset=0, y_offset=0):
        last_level = last_unlocked
        if self.grow_course:
            last_level -= 1
            color = self.SHELL_COLORS[last_level // 18 + 1]
            position = constants.FULL_MIDDLE_INT
            position = (position[0] + x_offset, position[1] + y_offset)
            pygame.draw.circle(surface, color, position, int(self.grow_radius))

            level_center = self.level_center(last_level)

            text = render_level_number(last_level + 1)
            text_x = level_center[0] - (text.get_width() / 2) + x_offset + 2
            text_y = level_center[1] - (text.get_height() / 2) + y_offset + 3
            text.set_alpha(self.level_alpha)

            surface.blit(text, (text_x, text_y))

        last_unlocked_course = (last_level - 1) // LEVELS_PER_COURSE

        position = (constants.FULL_WIDTH // 2, constants.FULL_HEIGHT // 2)
        position = (position[0] + x_offset, position[1] + y_offset)
        circle_index = last_unlocked_course + 2
        for color in reversed(self.SHELL_COLORS[:last_unlocked_course + 2]):
            circle_index -= 1
            radius = self.CIRCLE_RADII[circle_index]
            pygame.draw.circle(surface, color, position, radius)

        course_num = -1
        for level in range(last_level):
            if level % LEVELS_PER_COURSE == 0:
                course_num += 1

            level_center = self.level_center(level)

            text = render_level_number(level + 1)
            text_x = level_center[0] - (text.get_width() / 2) + x_offset + 2
            text_y = level_center[1] - (text.get_height() / 2) + y_offset + 3

            if self.selected_level != -1:
                hovered_level = self.selected_level
            else:
                hovered_level = self.mouse_level

            if not self.grow_course and level == hovered_level:
                text_y += 3

                # Draws a circle around the selected level
                # color = constants.WHITE
                # position = self.level_center(self.mouse_level)
                # pygame.draw.circle(surface, color, position, self.BUTTON_RADIUS, 2)

            surface.blit(text, (text_x, text_y))

        if self.selected_level != -1:
            level = self.selected_level
            thumbnail_disabled = False
        elif self.mouse_level != -1:
            level = self.mouse_level
            thumbnail_disabled = self.show_credits or self.disable_clicking
        else:
            level = -1
            thumbnail_disabled = True

        is_valid_level = level != -1 and level < len(self.block_layers)
        if is_valid_level and not thumbnail_disabled:
            # position = constants.FULL_MIDDLE_INT
            # pygame.draw.circle(surface, constants.BLACK, position, 60)

            layer = self.block_layers[level]
            x = constants.FULL_MIDDLE[0] + x_offset
            y = constants.FULL_MIDDLE[1] + y_offset
            x -= levels.WIDTH * 3 / 2
            y -= levels.HEIGHT * 3 / 2
            layer.draw_thumbnail(surface, (x, y), constants.BLACK, 3)

        if self.show_credits:
            x = SCREEN_LEFT + game_title_x + x_offset
            y = SCREEN_TOP + game_title_y + y_offset - 6
            surface.blit(game_title, (x, y))

            x = constants.FULL_MIDDLE[0] - 44 + x_offset
            y = constants.FULL_MIDDLE[1] + 12 + y_offset
            surface.blit(logo_name_small, (x, y))

            x = constants.FULL_MIDDLE[0] - 74 + x_offset
            y = constants.FULL_MIDDLE[1] + 22 + y_offset
            surface.blit(logo_bird_small.get_now_frame(), (x, y))
            logo_bird_small.delay_next(10)

    def draw_credits_options(self, surface, x_offset=0, y_offset=0):
        x = self.CREDITS_X + x_offset
        y = self.CREDITS_Y + y_offset
        surface.blit(self.CREDITS_TEXT, (x, y))

        x = self.CREDITS_SUBTITLE_X + x_offset
        y = self.CREDITS_SUBTITLE_Y + y_offset
        surface.blit(self.CREDITS_SUBTITLE, (x, y))

        # x = self.LOGO_BIRD_X + x_offset
        # y = self.LOGO_BIRD_Y + y_offset
        # surface.blit(logo_bird.get_now_frame(), (x, y))
        #
        # x = self.LOGO_NAME_X + x_offset
        # y = self.LOGO_NAME_Y + y_offset
        # surface.blit(logo_name, (x, y))

    def draw_editor(self, surface, x_offset=0, y_offset=0):
        if self.mouse_level != -1:
            selected_level = self.mouse_level
            thumbnail_disabled = self.disable_clicking

        elif self.selected_level != -1:
            selected_level = self.selected_level
            thumbnail_disabled = False

        else:
            selected_level = -1
            thumbnail_disabled = True

        for level in range(LAST_LEVEL + 1, self.last_editor_level):
            text = graphics.textify(str(level + 1))
            level_center = self.editor_level_center(level)
            x = level_center[0] - (text.get_width() // 2) + x_offset
            y = level_center[1] - (text.get_height() // 2) + y_offset

            if level == selected_level:
                y += 3

            surface.blit(text, (x, y))

        x = self.add_x + x_offset
        y = self.add_y + y_offset
        if self.editor_button == self.ADD:
            y += 3
        surface.blit(self.ADD_TEXT, (x, y))

        is_valid_level = 0 <= selected_level < len(self.block_layers)
        if is_valid_level and not thumbnail_disabled:
            layer = self.block_layers[selected_level]
            x = self.EDITOR_THUMBNAIL_X + x_offset
            y = self.EDITOR_THUMBNAIL_Y + y_offset

            layer.draw_thumbnail(surface, (x, y), constants.WHITE, 3)

            for text_num, text in enumerate(self.EDITOR_TEXTS):
                if text_num + 1 == self.LEVEL_LEFT:
                    if selected_level <= LAST_LEVEL + 1:
                        continue
                elif text_num + 1 == self.LEVEL_RIGHT:
                    if selected_level >= self.last_editor_level - 1:
                        continue
                x = self.EDITOR_TEXTS_X[text_num] + x_offset
                y = self.EDITOR_TEXTS_Y[text_num] + y_offset
                if self.editor_button - 1 == text_num:
                    y += 3
                surface.blit(text, (x, y))

        x = self.EDITOR_NOTE_X + x_offset
        y = self.EDITOR_NOTE_Y + y_offset
        surface.blit(self.EDITOR_NOTE_TEXT, (x, y))

        if self.in_transition and self.arrow_alpha < 255:
            self.editor_note_cover.set_alpha(255 - self.arrow_alpha)
            surface.blit(self.editor_note_cover, (x, y))

    def level_center(self, level_num):
        course_num = level_num // LEVELS_PER_COURSE
        level_in_course = level_num % LEVELS_PER_COURSE

        angle = math.pi * 2 * (level_in_course / LEVELS_PER_COURSE)
        angle -= math.pi / 2
        angle += self.angle_offsets[course_num]

        x = self.BUTTON_RING_RADII[course_num] * math.cos(angle)
        y = self.BUTTON_RING_RADII[course_num] * math.sin(angle)
        x += constants.FULL_MIDDLE[0]
        y += constants.FULL_MIDDLE[1]

        return int(x), int(y)

    def editor_level_center(self, level_num):
        column = (level_num - LAST_LEVEL - 1) % self.EDITOR_LEVELS_IN_ROW
        row = (level_num - LAST_LEVEL - 1) // self.EDITOR_LEVELS_IN_ROW
        x = self.EDITOR_LEFT + self.EDITOR_HORIZONTAL_SPACING * column
        y = self.EDITOR_TOP + self.EDITOR_VERTICAL_SPACING * row

        return x, y

    def touching_level(self, point):
        distance = geometry.distance(constants.FULL_MIDDLE, point)

        if distance < 100.0:
            return -1

        for course_num, radius in enumerate(self.CIRCLE_RADII[1:]):
            if distance < radius:
                course = course_num
                break
        else:
            return -1

        course_angle = (math.pi * 2.0 / LEVELS_PER_COURSE)

        angle = geometry.angle_between(constants.FULL_MIDDLE, point)
        angle += math.pi / 2
        angle -= self.angle_offsets[course_num]
        angle += course_angle / 2
        if angle < 0.0:
            angle += math.pi * 2
        level_in_course = int(angle / course_angle)
        level = level_in_course + course * LEVELS_PER_COURSE

        point_distance = geometry.distance(point, self.level_center(level))
        if point_distance < self.BUTTON_RADIUS:
            return level
        return -1

    def touching_editor_level(self, position):
        column = (position[0] - self.EDITOR_LEFT)
        column += self.EDITOR_HORIZONTAL_SPACING // 2
        column //= self.EDITOR_HORIZONTAL_SPACING

        row = (position[1] - self.EDITOR_TOP)
        row += self.EDITOR_VERTICAL_SPACING // 2
        row //= self.EDITOR_VERTICAL_SPACING

        level = row * self.EDITOR_LEVELS_IN_ROW + column + LAST_LEVEL + 1

        point1 = self.editor_level_center(level)
        if not point1:
            return -1
        point2 = position

        if geometry.distance(point1, point2) <= self.BUTTON_RADIUS:
            return level
        else:
            return -1

    def init_grow_course(self):
        previous_course = (last_unlocked - 2) // 18
        self.grow_course = True
        self.grow_frame = 0
        self.level_alpha = 0
        self.grow_radius = self.CIRCLE_RADII[previous_course + 1]
        self.target_radius = self.CIRCLE_RADII[previous_course + 2]

        self.grow_a = float(self.grow_radius - self.target_radius)
        self.grow_a /= (self.PAUSE_LAST - self.GROW_LAST) ** 2

    def update_menu_buttons(self):
        # Detect collision with mouse
        if self.changing_page:
            self.mouse_arrow = 0
        else:
            mouse_x, mouse_y = events.mouse.position
            top = self.ARROW_Y + self.arrow_y_offset
            bottom = self.ARROW_Y + self.ARROW_HEIGHT + self.arrow_y_offset

            if top < mouse_y < bottom:
                left_left = self.LEFT_ARROW_X
                left_right = self.LEFT_ARROW_X + self.ARROW_WIDTH

                right_left = self.RIGHT_ARROW_X
                right_right = self.RIGHT_ARROW_X + self.ARROW_WIDTH

                if self.page != 0 and left_left < mouse_x < left_right:
                    self.mouse_arrow = self.LEFT
                elif self.page != 2 and right_left < mouse_x < right_right:
                    self.mouse_arrow = self.RIGHT
                else:
                    self.mouse_arrow = 0

            else:
                self.mouse_arrow = 0

        # Bob up and down
        self.arrow_y_offset = 2.9 * math.sin(3 * math.pi / 180 * self.arrow_frame)
        if self.arrow_frame >= 120:
            self.arrow_frame = 0
        else:
            self.arrow_frame += 1

        # Change opacity
        if self.show_arrows and self.arrow_alpha < 255:
            self.arrow_alpha += 20

            if self.arrow_alpha > 255:
                self.arrow_alpha = 255

        elif not self.show_arrows and self.arrow_alpha > 0:
            self.arrow_alpha -= 20

            if self.arrow_alpha < 0:
                self.arrow_alpha = 0

    def update_add_level(self):
        center = self.editor_level_center(self.last_editor_level)
        x = center[0] - self.ADD_WIDTH // 2
        y = center[1] - self.ADD_HEIGHT // 2
        self.add_x = x
        self.add_y = y
        self.add_rect = pygame.Rect(x, y, self.ADD_WIDTH, self.ADD_HEIGHT)

    def cover_title(self, surface):
        menu_temp_surface.fill(constants.TRANSPARENT)

        color = ball.SHELL_DEBUG_COLORS[ball.CENTER]
        radius = int((self.CIRCLE_RADII[0] - 10) * self.zoom_amount)
        position = constants.SCREEN_MIDDLE_INT
        pygame.draw.circle(menu_temp_surface, color, position, radius)

        circle_alpha = ((self.zoom_frame - 1) / (self.ZOOM_LENGTH // 2)) * 255
        if circle_alpha > 255:
            circle_alpha = 255
        menu_temp_surface.set_alpha(circle_alpha)

        surface.blit(menu_temp_surface, TOP_LEFT)

    def detect_editor_mouse_button(self):
        mouse_x = events.mouse.position[0]
        mouse_y = events.mouse.position[1]

        if self.EDITOR_TEXTS_BOXES[0].collidepoint(mouse_x, mouse_y):
            return self.PLAY
        if self.EDITOR_TEXTS_BOXES[1].collidepoint(mouse_x, mouse_y):
            return self.EDIT
        if self.EDITOR_TEXTS_BOXES[2].collidepoint(mouse_x, mouse_y):
            return self.DELETE
        if self.EDITOR_TEXTS_BOXES[3].collidepoint(mouse_x, mouse_y):
            return self.LEVEL_LEFT
        if self.EDITOR_TEXTS_BOXES[4].collidepoint(mouse_x, mouse_y):
            return self.LEVEL_RIGHT
        if self.add_rect.collidepoint(mouse_x, mouse_y):
            return self.ADD

        return 0


class PlayScreen:
    SLOWMO_MAX = 8.0  # the largest factor of slowmo possible
    SPEEDUP_FACTOR = 0.05  # how much the slowmo effect "wears off" each frame

    AIMER_LAYERS = 4

    RESTART_DELAY = 90

    def __init__(self):
        self.level = None
        self.slowmo_factor = 1.0  # the coefficient of time-slow.
        self.balls = []
        self.players = []
        self.start_ball = None
        self.level_num = 0

        # make sure you DONT DRAW THE RED BUTTONS ON BLOCK_SURFACE
        self.block_surface = graphics.new_surface(constants.SCREEN_SIZE)

        self.start_position = constants.SCREEN_MIDDLE
        self.end_open = False

        self.pause_exit = False
        self.transition = False
        self.end_ball = None

        self.unlocked = True

        restart_text = graphics.textify("Press R to restart.")
        exit_text = graphics.textify("Press ESC to exit.")
        self.restart_text = graphics.new_surface((restart_text.get_width(), 50))
        self.restart_text.blit(restart_text, (0, 0))
        self.restart_text.blit(exit_text, (5, 21))
        self.restart_cover = pygame.Surface(self.restart_text.get_size())
        self.restart_cover.fill(constants.BLACK)

        self.restart_timer = 0
        self.restart_alpha = 0
        self.RESTART_X = (FULL_WIDTH - self.restart_text.get_width()) // 2 + 3
        self.RESTART_Y = SCREEN_TOP + levels.PIXEL_HEIGHT + 10

        self.in_editor = False

    def update(self):
        mouse = events.mouse
        new_x = mouse.position[0] - SCREEN_LEFT
        new_y = mouse.position[1] - SCREEN_TOP
        mouse.position = (new_x, new_y)
        keys = events.keys

        if mouse.released and self.players[0].containing_shells:
            self.shoot_balls(mouse.position)
            self.slowmo_factor = 1.0

        if mouse.held and self.players[0].containing_shells:
            if mouse.clicked:
                self.slowmo_factor = self.SLOWMO_MAX

            if self.slowmo_factor > 1.0:
                self.slowmo_factor -= self.SPEEDUP_FACTOR

                if self.slowmo_factor < 1.0:
                    self.slowmo_factor = 1.0

            for player in self.players:
                player.rotate_towards(mouse.position, self.slowmo_factor)

        if keys.pressed_key == pygame.K_r:
            if mouse.held:
                self.reset_level(True)
            else:
                self.reset_level(False)

        elif keys.pressed_key == pygame.K_ESCAPE:
            self.transition = True
            self.pause_exit = True
            self.end_ball = self.players[0]

        greatest_speed = 0.0
        ball_index = len(self.balls)
        for ball_ in reversed(self.balls):
            ball_index -= 1
            if ball_.out_of_bounds():
                del self.balls[ball_index]
            else:
                ball_.check_collision(self.level, self.slowmo_factor)

                if self.level.pressed_buttons == self.level.total_buttons:
                    if ball_.touching_end:
                        self.transition = True
                        self.end_ball = ball_

                        if ball_.shell_type == ball.GHOST:
                            instrument = sound.ghost_instrument
                        elif ball_.shell_type == ball.FLOAT:
                            instrument = sound.float_instrument
                        else:
                            instrument = sound.normal_instrument

                        instrument.play(sound.CS3, 0.6)

                ball_.update_body(self.slowmo_factor)

                velocity = (ball_.x_velocity, ball_.y_velocity)
                greatest_speed = max(greatest_speed, geometry.magnitude(velocity))

        player_shells = 0
        for player in self.players:
            player_shells += len(player.containing_shells)

        if greatest_speed < 1.0 and player_shells == 0:
            if self.restart_timer < self.RESTART_DELAY:
                self.restart_timer += 1
            elif self.restart_alpha < 255:
                self.restart_alpha += 20

                if self.restart_alpha > 255:
                    self.restart_alpha = 255

                self.restart_cover.set_alpha(255 - self.restart_alpha)

        else:
            self.restart_timer = 0

        if not self.unlocked:
            if self.level.pressed_buttons == self.level.total_buttons:
                self.unlocked = True
                self.level.draw_debug_start_end(self.block_surface, (0, 0))

        graphics.update_ripples(self.slowmo_factor)

    def draw(self, surface, offset=(0, 0)):
        x = SCREEN_LEFT + offset[0]
        y = SCREEN_TOP + offset[1]
        surface.blit(self.block_surface, (x, y))
        self.level.draw_debug_layer(surface, levels.LAYER_BUTTONS, (x, y))

        if self.restart_timer >= self.RESTART_DELAY:
            restart_x = self.RESTART_X + offset[0]
            restart_y = self.RESTART_Y + offset[1]
            surface.blit(self.restart_text, (restart_x, restart_y))
            surface.blit(self.restart_cover, (restart_x, restart_y))

        graphics.draw_ripples(surface, offset)

        if events.mouse.held and self.players[0].containing_shells:
            self.draw_aimers(surface, offset)

        for ball_ in self.balls:
            ball_.draw_debug(surface, (x, y))

    def shoot_balls(self, position):
        """Shoots all player balls towards a specific position."""
        add_balls = []
        remove_balls = []
        for player in self.players:
            old_ball = player

            new_radius = player.radius - ball.SHELL_WIDTH
            new_shell = old_ball.containing_shells[0]
            new_ball = ball.Ball(player.position, new_radius, new_shell)

            new_ball.is_player = True

            new_ball.angle = old_ball.angle
            new_ball.containing_shells = old_ball.containing_shells[1:]

            if old_ball.shell_type == ball.CLONE:
                old_ball.shell_type = old_ball.containing_shells[0]
                old_ball.containing_shells = old_ball.containing_shells[1:]
                old_ball.radius = new_radius

            else:
                old_ball.is_player = False
                old_ball.containing_shells = []
                remove_balls.append(old_ball)

            add_balls.append(new_ball)

            new_ball.launch_towards(position)
            old_ball.x_velocity = -new_ball.x_velocity
            old_ball.y_velocity = -new_ball.y_velocity

        for player in remove_balls:
            self.players.remove(player)

        for player in add_balls:
            self.players.append(player)
            self.balls.append(player)

    def draw_aimers(self, surface, offset=(0, 0)):
        mouse_position = events.mouse.position
        for player in self.players:
            angle1 = geometry.angle_between(mouse_position, player.position)
            angle2 = angle1 + math.pi

            width = 2
            color = ball.SHELL_DEBUG_COLORS[player.shell_type]
            for layer in range(self.AIMER_LAYERS, 0, -1):
                magnitude = player.radius + layer ** 2

                diff1 = geometry.vector_to_difference(angle1, magnitude)
                diff2 = geometry.vector_to_difference(angle2, magnitude)
                point1 = (diff1[0] + player.x, diff1[1] + player.y)
                point2 = (diff2[0] + player.x, diff2[1] + player.y)
                point1 = (point1[0] + offset[0], point1[1] + offset[1])
                point2 = (point2[0] + offset[0], point2[1] + offset[1])
                point1 = graphics.screen_position(point1)
                point2 = graphics.screen_position(point2)
                pygame.draw.line(surface, color, point1, point2, width)

                width += 2

    def reset_level(self, slowmo=False):
        self.balls = [copy.deepcopy(self.start_ball)]
        self.players = [self.balls[0]]
        self.players[0].point_towards_end(self.level)
        columns = levels.WIDTH
        rows = levels.HEIGHT
        self.level.pressed_grid = [[False] * rows for _ in range(columns)]
        self.level.pressed_buttons = 0
        self.unlocked = False
        self.level.draw_debug_start_end(self.block_surface, (0, 0))
        self.restart_alpha = 0
        self.restart_cover.set_alpha(255)
        if slowmo:
            self.slowmo_factor = self.SLOWMO_MAX

    def load_level(self, level_num):
        """Prepares play_screen to play the given level.

        level_num is zero indexed, unlike the save file and in-game numbers.
        """
        self.block_surface.fill(constants.TRANSPARENT)
        self.slowmo_factor = 1.0

        self.level_num = level_num
        self.level = levels.load_level(level_num)

        block_layer = levels.LAYER_BLOCKS
        self.level.draw_debug_layer(self.block_surface, block_layer, (0, 0))
        self.level.draw_debug_start_end(self.block_surface, (0, 0))

        start_tile = self.level.start_tile
        position = levels.middle_pixel(start_tile)
        radius = ball.first_ball_radius(self.level)
        containing_shells = self.level.start_shells
        shell = containing_shells.pop(0)

        self.start_ball = ball.Ball(position, radius, shell)
        self.start_ball.is_player = True
        self.start_ball.containing_shells = containing_shells

        self.reset_level()


class LevelTransition:
    PAUSE_LENGTH = 30
    OUT_LENGTH = 60
    IN_LENGTH = 60
    SHELL_LENGTH = 13

    PAUSE_LAST = PAUSE_LENGTH
    OUT_LAST = PAUSE_LAST + OUT_LENGTH
    IN_LAST = OUT_LAST + IN_LENGTH

    LAST_RADIUS = 700
    LAST_WIDTH = 150

    GENERAL = 1
    MENU_TO_LEVEL = 2
    LEVEL_TO_LEVEL = 3
    LEVEL_TO_MENU = 4

    def __init__(self):
        self.previous_screen = 0
        self.next_screen = 0
        self.previous_level = None
        self.previous_balls = []

        self.something_to_level = False

        self.from_point = (0.0, 0.0)
        self.to_point = (0.0, 0.0)
        self.center = (0.0, 0.0)

        self.x_change = 0.0
        self.y_change = 0.0

        # finds the value a in y = a(x - r)(x - s) form
        # x and y are based off of the vertex, at maximum radius/width
        denominator = (self.OUT_LAST - self.PAUSE_LAST)
        denominator *= (self.OUT_LAST - self.IN_LAST)

        self.radius_a = self.LAST_RADIUS / denominator
        self.width_a = self.LAST_WIDTH / denominator

        self.frame = 0
        self.radius = 0.0
        self.width = 0.0

        self.transparency_temp = graphics.new_surface(constants.SCREEN_SIZE)

        self.shell_count = 0
        self.color = constants.WHITE

        self.done = False

        self.sound_whoosh = sound.load("transition")
        self.sound_whoosh.set_volume(0.7)

        self.type = 0

    def update(self):
        if self.frame <= self.PAUSE_LAST:
            pass
        elif self.frame <= self.IN_LAST:
            center_x = self.center[0] + self.x_change
            center_y = self.center[1] + self.y_change
            self.center = (center_x, center_y)

            # equation is the (x - r)(x - s) part.
            equation = self.frame - self.PAUSE_LAST
            equation *= self.frame - self.IN_LAST
            self.radius = self.radius_a * equation
            self.width = self.width_a * equation

        elif self.type == self.LEVEL_TO_LEVEL or self.type == self.MENU_TO_LEVEL:
            if (self.frame - self.IN_LAST) % self.SHELL_LENGTH == 0:
                self.shell_count += 1
                total_shells = len(play_screen.players[0].containing_shells)

                if self.shell_count > total_shells:
                    self.done = True
                elif self.shell_count < 10:
                    instrument = sound.normal_instrument
                    instrument.play(sound.grow_notes[self.shell_count - 1], 0.7)

        else:
            self.done = True

        if self.frame == self.PAUSE_LAST:
            self.sound_whoosh.play()

        self.frame += 1

    def draw(self, surface):
        if self.frame <= self.PAUSE_LAST:
            self.draw_previous(surface)

        elif self.frame <= self.OUT_LAST:
            shake_position = (random.randint(-3, 3), random.randint(-3, 3))
            self.draw_previous(surface, shake_position)

            center = (int(self.center[0]), int(self.center[1]))
            radius = int(self.radius)
            width = int(self.width)
            pygame.draw.circle(surface, self.color, center, radius, width)

        elif self.frame <= self.IN_LAST:
            shake_position = (random.randint(-3, 3), random.randint(-3, 3))
            self.draw_previous(surface, shake_position)

            center = (int(self.center[0]), int(self.center[1]))
            center = (center[0] - SCREEN_LEFT, center[1] - SCREEN_TOP)

            radius = int(self.radius)
            width = int(self.width)

            self.transparency_temp.fill(constants.BLACK)
            self.draw_next(self.transparency_temp, (-SCREEN_LEFT, -SCREEN_TOP))
            color = constants.TRANSPARENT
            pygame.draw.circle(self.transparency_temp, color, center, radius)

            position = graphics.screen_position(shake_position)
            surface.blit(self.transparency_temp, position)

            center = (center[0] + SCREEN_LEFT, center[1] + SCREEN_TOP)
            pygame.draw.circle(surface, self.color, center, radius, width)

        elif self.type == self.LEVEL_TO_LEVEL or self.type == self.MENU_TO_LEVEL:
            self.draw_next(surface)

        else:  # level-menu transition carries on for one more frame
            self.draw_next(surface)

    def draw_previous(self, surface, position=(0, 0)):
        if self.previous_screen == MENU:
            main_menu.draw(surface, position)
        elif self.previous_screen == PLAY:
            level_x = position[0] + SCREEN_LEFT
            level_y = position[1] + SCREEN_TOP

            level = self.previous_level
            layer = levels.LAYER_BLOCKS
            level.draw_debug_layer(surface, layer, (level_x, level_y))

            layer = levels.LAYER_BUTTONS
            level.draw_debug_layer(surface, layer, (level_x, level_y))
            level.draw_debug_start_end(surface, (level_x, level_y))

            graphics.draw_ripples(surface, position)

            for ball_ in self.previous_balls:
                ball_.draw_debug(surface, (level_x, level_y))

    def draw_next(self, surface, position=(0, 0)):
        if self.next_screen == MENU:
            main_menu.draw(surface, position)
        elif self.next_screen == PLAY:
            level_x = position[0] + SCREEN_LEFT
            level_y = position[1] + SCREEN_TOP

            level = play_screen.level
            layer = levels.LAYER_BLOCKS
            level.draw_debug_layer(surface, layer, (level_x, level_y))

            layer = levels.LAYER_BUTTONS
            level.draw_debug_layer(surface, layer, (level_x, level_y))
            level.draw_debug_start_end(surface, (level_x, level_y))

            shells = self.shell_count + 1
            player = play_screen.players[0]
            player.draw_debug(surface, (level_x, level_y), shells)

    def set_from_point(self, position):
        self.from_point = (position[0] + SCREEN_LEFT, position[1] + SCREEN_TOP)

    def set_to_point(self, position):
        self.to_point = (position[0] + SCREEN_LEFT, position[1] + SCREEN_TOP)

    def init_menu_to_level(self):
        """All of these init functions reach into the main_menu and play_screen
        global objects.
        """
        play_screen.load_level(main_menu.selected_level)

        level = play_screen.level
        self.type = self.MENU_TO_LEVEL
        self.something_to_level = True

        self.frame = 0
        self.previous_screen = MENU
        self.next_screen = PLAY

        if main_menu.selected_level < LAST_LEVEL:
            from_point = main_menu.level_center(main_menu.selected_level)

            menu_course = main_menu.selected_level // LEVELS_PER_COURSE
            self.color = ball.SHELL_DEBUG_COLORS[menu_course + 1]
        else:
            from_point = main_menu.editor_level_center(main_menu.selected_level)
            self.color = ball.SHELL_DEBUG_COLORS[ball.CENTER]

        to_point = levels.middle_pixel(level.start_tile)
        to_point = graphics.screen_position(to_point)

        length = (self.OUT_LENGTH + self.IN_LENGTH)
        self.x_change = (to_point[0] - from_point[0]) / length
        self.y_change = (to_point[1] - from_point[1]) / length
        self.center = from_point

        self.shell_count = 0

        main_menu.show_arrows = False

    def init_level_to_level(self):
        self.type = self.LEVEL_TO_LEVEL
        self.something_to_level = True

        self.frame = 0
        self.previous_screen = PLAY
        self.next_screen = PLAY

        self.previous_level = play_screen.level
        self.previous_balls = play_screen.balls

        next_level = levels.load_level(play_screen.level_num + 1)
        end_position = play_screen.end_ball.position

        from_point = graphics.screen_position(end_position)
        to_point = levels.middle_pixel(next_level.start_tile)
        to_point = graphics.screen_position(to_point)

        length = (self.OUT_LENGTH + self.IN_LENGTH)
        self.x_change = (to_point[0] - from_point[0]) / length
        self.y_change = (to_point[1] - from_point[1]) / length
        self.center = from_point

        self.color = ball.SHELL_DEBUG_COLORS[play_screen.end_ball.shell_type]

        self.shell_count = 0

        play_screen.load_level(play_screen.level_num + 1)

    def init_level_to_menu(self):
        if not play_screen.pause_exit:
            if (play_screen.level_num + 1) % LEVELS_PER_COURSE == 0:
                play_screen.level_num += 1

        self.type = self.LEVEL_TO_MENU
        self.something_to_level = False

        self.frame = 0
        self.previous_screen = PLAY
        self.next_screen = MENU

        self.previous_level = play_screen.level
        self.previous_balls = play_screen.balls

        end_position = play_screen.end_ball.position

        from_point = graphics.screen_position(end_position)
        to_point = constants.FULL_MIDDLE

        length = (self.OUT_LENGTH + self.IN_LENGTH)
        self.x_change = (to_point[0] - from_point[0]) / length
        self.y_change = (to_point[1] - from_point[1]) / length
        self.center = from_point

        self.color = ball.SHELL_DEBUG_COLORS[play_screen.end_ball.shell_type]


def check_level_menu_transition():
    if play_screen.pause_exit:
        return True

    if play_screen.level_num + 1 == last_unlocked:
        if last_unlocked % LEVELS_PER_COURSE == 0:
            return True

    if play_screen.level_num == LAST_LEVEL:
        return True

    if play_screen.level_num + 1 == main_menu.last_editor_level:
        return True

    return False


main_menu = MenuScreen()
main_menu.zoom_state = main_menu.ZOOMED

play_screen = PlayScreen()

transition = LevelTransition()

MENU = 0
PLAY = 1
TRANSITION = 2
EDITOR = 3
# play_screen.load_level(24)
current_screen = MENU  # change back to MENU later

# Logo loop
LOGO_WIDTH = 284
LOGO_HEIGHT = 52
LOGO_BIRD_X = (FULL_WIDTH - LOGO_WIDTH) // 2
LOGO_BIRD_Y = (FULL_HEIGHT - LOGO_HEIGHT) // 2
LOGO_NAME_X = LOGO_BIRD_X + 64
LOGO_NAME_Y = LOGO_BIRD_Y - 12

graphics.fader.set_alpha(0)
graphics.fader.fade_to(255)
# sound.intro_jingle.play()
#
# for frame in range(270):
#     events.update()
#
#     final_display.blit(logo_bird.get_now_frame(), (LOGO_BIRD_X, LOGO_BIRD_Y))
#     final_display.blit(logo_name, (LOGO_NAME_X, LOGO_NAME_Y))
#
#     logo_bird.delay_next(9)
#
#     if frame == 225:
#         graphics.fader.fade_to(0)
#
#     graphics.fader.update()
#     graphics.fader.draw(final_display)
#     screen_update(60)

# Game loop
graphics.fader.fade_to(255)
sound.play_music()

while True:
    events.update()
    sound.update()
    debug.debug(pygame.mixer.music.get_pos())

    if current_screen == PLAY:
        play_screen.update()
        play_screen.draw(final_display)

        if play_screen.transition and play_screen.in_editor:
            play_screen.transition = False
            play_screen.in_editor = False
            current_screen = EDITOR

        elif play_screen.transition:
            play_screen.transition = False

            current_screen = TRANSITION

            if check_level_menu_transition():
                if play_screen.pause_exit:
                    if play_screen.level_num < LAST_LEVEL:
                        main_menu.page = main_menu.LEVEL_SELECT
                        transition.init_level_to_menu()
                    else:
                        main_menu.page = main_menu.LEVEL_EDITOR
                        transition.init_level_to_menu()

                else:
                    if play_screen.level_num > LAST_LEVEL:
                        main_menu.page = main_menu.LEVEL_EDITOR
                        transition.init_level_to_menu()

                    elif play_screen.level_num == LAST_LEVEL:
                        main_menu.show_credits = True
                        main_menu.page = main_menu.LEVEL_SELECT
                        transition.init_level_to_menu()

                    else:
                        main_menu.page = main_menu.LEVEL_SELECT
                        transition.init_level_to_menu()
                        main_menu.init_grow_course()
            else:
                transition.init_level_to_level()

            if not play_screen.pause_exit:
                if last_unlocked < play_screen.level_num + 1:
                    if play_screen.level_num - 1 < LAST_LEVEL:
                        last_unlocked = play_screen.level_num + 1
                        save_data = open("Easily Editable Save Data.txt", 'w')
                        save_data.write(str(last_unlocked) + "\n")
                        save_data.close()

            else:
                play_screen.pause_exit = False

    elif current_screen == MENU:
        main_menu.update()
        if main_menu.zoom_state == main_menu.NORMAL:
            main_menu.draw(final_display)
        else:
            main_menu.draw_zoomed(final_display)

            if main_menu.zoom_state == main_menu.ZOOMING_OUT:
                main_menu.cover_title(final_display)

        if main_menu.switch_to_level:
            main_menu.switch_to_level = False
            main_menu.disable_clicking = True

            main_menu.mouse_level = -1
            current_screen = TRANSITION

            transition.init_menu_to_level()

        elif main_menu.switch_to_editor:
            main_menu.switch_to_editor = False
            main_menu.in_transition = True

            editor.editor.load_level(main_menu.selected_level)
            editor.editor.init_editor_ui()
            current_screen = EDITOR

    elif current_screen == TRANSITION:
        transition.update()
        if transition.previous_screen == MENU or transition.next_screen == MENU:
            main_menu.update()
        transition.draw(final_display)

        if transition.done:
            transition.done = False
            if transition.previous_screen == MENU:
                main_menu.selected_level = -1

            if transition.something_to_level:
                current_screen = PLAY
                if events.mouse.held:
                    play_screen.slowmo_factor = play_screen.SLOWMO_MAX
            elif transition.type == transition.LEVEL_TO_MENU:
                current_screen = MENU
                main_menu.disable_clicking = False
                main_menu.show_arrows = True
            graphics.clear_ripples()

    elif current_screen == EDITOR:
        editor.editor.update()
        editor.editor.draw(final_display)

        if editor.editor.switch_to_menu:
            editor.editor.switch_to_menu = False
            editor.editor.undos = []

            main_menu.block_layers[main_menu.selected_level] = editor.editor.level.layers[levels.LAYER_BLOCKS]
            main_menu.selected_level = -1

            current_screen = MENU

        elif editor.editor.switch_to_player:
            editor.editor.switch_to_player = False
            editor.editor.undos = []
            editor.editor.reset_changes_grid()

            play_screen.load_level(main_menu.selected_level)
            play_screen.in_editor = True

            current_screen = PLAY

    graphics.fader.update()
    graphics.fader.draw(final_display)

    debug.debug(clock.get_fps())
    debug.debug(current_screen)
    debug.debug(main_menu.grow_frame)
    debug.debug(main_menu.mouse_arrow)
    debug.debug(main_menu.mouse_level)
    debug.debug(main_menu.selected_level)

    debug.draw(final_display)

    # if events.mouse.held:
    #     screen_update(2)
    # else:
    screen_update(60)
