from copy import copy
import pygame
from grid import Grid
from tetraminos import Tetramino


class ActiveTetramino(Tetramino):
    def __init__(self, tetramino: Tetramino, x=4, y=2):
        self.x = x
        self.y = y
        self.rotation = 0
        self.base_tetramino = tetramino
        super().__init__(tetramino.color, tetramino.shapes, tetramino.rotation_offsets)

    def move_left(self) -> bool:
        self.x -= 1
        if not Grid.get().fits(self):
            self.x += 1
            return False
        return True

    def move_right(self) -> bool:
        self.x += 1
        if not Grid.get().fits(self):
            self.x -= 1
            return False
        return True

    def move_down(self) -> bool:
        self.y += 1
        if not Grid.get().fits(self):
            self.y -= 1
            return False
        return True

    def rotate_cw(self) -> bool:
        self.rotation = (self.rotation + 1) % 4
        if not Grid.get().fits(self):
            self.rotation = (self.rotation + 3) % 4
            return False
        return True

    def rotate_ccw(self) -> bool:
        self.rotation = (self.rotation + 3) % 4
        if not Grid.get().fits(self):
            self.rotation = (self.rotation + 1) % 4
            return False
        return True

    def rotate_180(self) -> bool:
        self.rotation = (self.rotation + 2) % 4
        if not Grid.get().fits(self):
            self.rotation = (self.rotation + 2) % 4
            return False
        return True

    def get_positions(self) -> list[tuple[int, int]]:
        positions = []
        shape = self.shapes[self.rotation]

        for i, line in enumerate(shape):
            row = list(line)
            for j, column in enumerate(row):
                if column == "0":
                    positions.append((self.x + j, self.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions

    def draw(self, surface: pygame.Surface, tile_size: int):
        for x, y in self.get_positions():
            pygame.draw.rect(
                surface,
                self.color,
                (
                    x * tile_size,
                    y * tile_size,
                    tile_size,
                    tile_size,
                ),
                0,
            )

    def draw_ghost(self, surface: pygame.Surface, tile_size: int):
        ghost = copy(self)
        ghost.color = (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
        while ghost.move_down():
            pass
        ghost.draw(surface, tile_size)
