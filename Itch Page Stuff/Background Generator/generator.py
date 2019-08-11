import levels
import pygame
import random

pygame.init()

all_levels = [levels.load_level(num) for num in range(54)]
all_levels.pop(53)  # Removes "Thank You For Playing" Level
all_levels.pop(48)  # Removes third image on itch ("Orange Timer" level)
all_levels.pop(14)  # Removes second image on itch ("X" level)
all_levels.pop(6)  # Removes the mostly empty "One Shot" level
all_levels.pop(3)  # Removes first image on itch ("Arrow" level)

MARGIN = 50
surface = pygame.Surface((500 * 4 + MARGIN * 5, 500 * 7 + MARGIN * 8))
surface.set_colorkey((0, 255, 0))
surface_2 = pygame.Surface((500 * 4 + MARGIN * 5, 500 * 7 + MARGIN * 8))
surface_2.fill((0, 0, 0))

for iteration in range(28):
    level = all_levels.pop(random.randint(0, len(all_levels) - 1))

    row = iteration // 4
    column = iteration % 4
    x = column * (500 + MARGIN) + MARGIN
    y = row * (500 + MARGIN) + MARGIN

    level.draw_debug(surface, (x, y))

surface_2.blit(surface, (0, 0))

pygame.image.save(surface_2, "background.png")
