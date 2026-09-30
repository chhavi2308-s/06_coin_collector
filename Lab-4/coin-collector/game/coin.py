"""
Coin: a static collectible circle. Drawn as a circle, hit-tested as a
bounding square around it.

Three kinds exist (bronze, silver, gold). COIN_TYPES is the single place
that defines each kind's value, color and how often it spawns.
"""

import pygame

# name -> value, color, spawn weight (relative; weights sum to 100 so gold = 15%)
COIN_TYPES = {
    "bronze": {"value": 1, "color": (205, 127, 50),  "weight": 60},
    "silver": {"value": 3, "color": (200, 205, 215), "weight": 25},
    "gold":   {"value": 5, "color": (255, 215, 0),   "weight": 15},
}


class Coin:
    def __init__(self, x, y, kind="bronze", radius=12):
        if kind not in COIN_TYPES:
            raise ValueError(f"Unknown coin kind: {kind!r}")
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.value = COIN_TYPES[kind]["value"]
        self.color = COIN_TYPES[kind]["color"]

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )