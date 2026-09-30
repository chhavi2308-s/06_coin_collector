"""
GameEngine: owns the player, coins, obstacles, lives and the round timer.

Coins come in three kinds (bronze / silver / gold, see game/coin.py) and
are spawned as a weighted random mix: mostly bronze, some silver, ~15% gold.

Coin collection: each frame, `update` asks check_collection which coins the
player is overlapping, adds their value to the score, and then removes them
from the coin list so every coin is collected exactly once.

Obstacles: red squares placed at start, never on the player or a coin.
Touching one costs a life, then the player is invincible (and blinking) for
INVINCIBILITY_MS so a single touch can't drain every life at once.

Round: lasts ROUND_SECONDS. It ends when the timer hits 0 or lives hit 0,
whichever comes first. Then gameplay stops and a Game Over screen shows the
final score. `restart()` resets everything for a new round.
"""

import math
import random
import pygame

from game.player import Player
from game.coin import Coin, COIN_TYPES
from game.obstacle import Obstacle
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT

NUM_COINS = 10
NUM_OBSTACLES = 5
OBSTACLE_SIZE = 30
STARTING_LIVES = 3
INVINCIBILITY_MS = 1000
BLINK_MS = 100  # player toggles visible/hidden every BLINK_MS while invincible
ROUND_SECONDS = 30

# Precompute kinds and weights once for random.choices.
_KINDS = list(COIN_TYPES.keys())
_WEIGHTS = [COIN_TYPES[k]["weight"] for k in _KINDS]


class GameEngine:
    def __init__(self):
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]
        # Obstacles are spawned after the player and coins so they can avoid them.
        self.obstacles = self._spawn_obstacles()
        self.score = 0
        self.lives = STARTING_LIVES
        self.invincible_until = 0  # pygame ticks (ms); 0 means not invincible
        self.game_over = False
        self.game_over_reason = ""
        self.round_start = pygame.time.get_ticks()
        self.time_left = ROUND_SECONDS

    def restart(self):
        """Reset score, lives, timer, coins and obstacles for a new round."""
        self.__init__()

    def _random_coin(self):
        x = random.randint(30, WIDTH - 30)
        y = random.randint(30, HEIGHT - 30)
        kind = random.choices(_KINDS, weights=_WEIGHTS, k=1)[0]
        return Coin(x=x, y=y, kind=kind, radius=12)

    def _spawn_obstacles(self):
        """
        Places up to NUM_OBSTACLES obstacles fully inside the play area, with
        a clear zone around the player's start position and a small gap
        around every coin and every other obstacle. If a spot can't be found
        after many tries, that obstacle is skipped rather than looping forever.
        """
        keep_out = [self.player.get_rect().inflate(100, 100)]
        keep_out += [c.get_rect().inflate(16, 16) for c in self.coins]

        obstacles = []
        half = OBSTACLE_SIZE // 2
        for _ in range(NUM_OBSTACLES):
            for _attempt in range(200):
                x = random.randint(half, WIDTH - half)
                y = random.randint(half, HEIGHT - half)
                candidate = Obstacle(x=x, y=y, size=OBSTACLE_SIZE)
                rect = candidate.get_rect()
                if any(rect.colliderect(r) for r in keep_out):
                    continue
                if any(rect.colliderect(o.get_rect().inflate(10, 10)) for o in obstacles):
                    continue
                obstacles.append(candidate)
                break
        return obstacles

    def _is_invincible(self):
        return pygame.time.get_ticks() < self.invincible_until

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed
        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return

        # --- timer: round ends when it reaches 0 ---
        elapsed_ms = pygame.time.get_ticks() - self.round_start
        remaining_ms = ROUND_SECONDS * 1000 - elapsed_ms
        if remaining_ms <= 0:
            self.time_left = 0
            self.game_over = True
            self.game_over_reason = "Time's up!"
            return
        self.time_left = math.ceil(remaining_ms / 1000)

        # --- coins: score each collected coin once, then remove it ---
        collected = check_collection(self.player, self.coins)
        for coin in collected:
            self.score += coin.value

        # Rebuild the list (rather than calling remove() inside a loop over
        # it) to avoid mutating self.coins while iterating.
        if collected:
            collected_ids = {id(coin) for coin in collected}
            self.coins = [c for c in self.coins if id(c) not in collected_ids]

        # --- obstacles: lose one life per hit, then a grace period ---
        if not self._is_invincible():
            player_rect = self.player.get_rect()
            if any(player_rect.colliderect(o.get_rect()) for o in self.obstacles):
                self.lives -= 1
                if self.lives <= 0:
                    self.lives = 0
                    self.game_over = True
                    self.game_over_reason = "Out of lives!"
                else:
                    self.invincible_until = pygame.time.get_ticks() + INVINCIBILITY_MS

    def draw(self, surface, font, big_font):
        from game import renderer

        # Blink while invincible: hidden on alternate BLINK_MS slices.
        now = pygame.time.get_ticks()
        blinking_off = self._is_invincible() and (now // BLINK_MS) % 2 == 0

        renderer.draw_scene(
            surface, self.player, self.coins, self.obstacles,
            player_visible=not blinking_off,
        )
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_timer(surface, font, self.time_left)
        renderer.draw_lives(surface, font, self.lives)
        if self.game_over:
            renderer.draw_game_over(
                surface, font, big_font, self.score, self.game_over_reason
            )