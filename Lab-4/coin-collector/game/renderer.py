"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (35, 45, 35)
COLOR_PLAYER = (80, 180, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_WARNING = (255, 90, 90)
COLOR_BANNER = (255, 220, 80)


def draw_scene(surface, player, coins, obstacles=(), player_visible=True):
    """
    Draws the background, coins, obstacles and (unless player_visible is
    False, used for the invincibility blink) the player.
    """
    surface.fill(COLOR_BG)
    for coin in coins:
        pygame.draw.circle(surface, coin.color, (int(coin.x), int(coin.y)), coin.radius)
    for obstacle in obstacles:
        pygame.draw.rect(surface, obstacle.color, obstacle.get_rect())
    if player_visible:
        pygame.draw.rect(surface, COLOR_PLAYER, player.get_rect(), border_radius=4)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_lives(surface, font, lives):
    """Draws 'Lives: N' in the top-right corner."""
    surf = font.render(f"Lives: {lives}", True, COLOR_TEXT)
    rect = surf.get_rect(topright=(surface.get_width() - 10, 10))
    surface.blit(surf, rect)


def draw_timer(surface, font, seconds_left):
    """Draws 'Time: N' at the top center; turns red for the last 5 seconds."""
    color = COLOR_WARNING if seconds_left <= 5 else COLOR_TEXT
    surf = font.render(f"Time: {seconds_left}", True, color)
    rect = surf.get_rect(midtop=(surface.get_width() // 2, 10))
    surface.blit(surf, rect)


def draw_game_over(surface, font, big_font, score, reason):
    """Dims the scene and shows the Game Over screen with the final score."""
    w, h = surface.get_size()

    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    lines = [
        (big_font, "GAME OVER", COLOR_BANNER, -70),
        (font, reason, COLOR_WARNING, -25),
        (big_font, f"Final score: {score}", COLOR_TEXT, 20),
        (font, "Press R to play again", COLOR_TEXT, 75),
    ]
    for f, text, color, dy in lines:
        surf = f.render(text, True, color)
        rect = surf.get_rect(center=(w // 2, h // 2 + dy))
        surface.blit(surf, rect)