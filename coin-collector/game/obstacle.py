"""
Obstacle: a static red square. Touching it costs the player a life
(see GameEngine.update). Positioned by its center, like Player and Coin.
"""

import pygame


class Obstacle:
    def __init__(self, x, y, size=30, color=(220, 50, 50)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2), int(self.y - self.size / 2),
            self.size, self.size,
        )