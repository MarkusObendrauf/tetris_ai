from functools import cache

import pygame


class Grid:
    HEIGHT = 20
    WIDTH = 10

    def __init__(self):
        self.grid = [[(0, 0, 0) for _ in range(Grid.WIDTH)] for _ in range(Grid.HEIGHT)]

    @staticmethod
    @cache  # singleton
    def get():
        return Grid()

    def insert_piece(self, active_tetramino):
        for x, y in active_tetramino.get_positions():
            self.grid[y][x] = active_tetramino.color

    def fits(self, active_tetramino):
        for x, y in active_tetramino.get_positions():
            if y >= Grid.HEIGHT:
                return False
            if x >= Grid.WIDTH or x < 0:
                return False
            if y >= 0 and self.grid[y][x] != (0, 0, 0):
                return False
        return True

    def clear_rows(self):
        for i, row in enumerate(self.grid):
            row = self.grid[i]
            if (0, 0, 0) not in row:
                del self.grid[i]
                self.grid.insert(0, [(0, 0, 0) for _ in range(Grid.WIDTH)])

    def draw(self, surface: pygame.Surface, tile_size: int):
        for i in range(Grid.HEIGHT):
            for j in range(Grid.WIDTH):
                pygame.draw.rect(
                    surface,
                    self.grid[i][j],
                    (
                        j * tile_size,
                        i * tile_size,
                        tile_size,
                        tile_size,
                    ),
                    0,
                )

    def draw_gridlines(self, surface: pygame.Surface, tile_size: int):
        for i in range(Grid.HEIGHT):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (0, i * tile_size),
                (Grid.WIDTH * tile_size, i * tile_size),
            )
            for j in range(Grid.WIDTH):
                pygame.draw.line(
                    surface,
                    (128, 128, 128),
                    (j * tile_size, 0),
                    (j * tile_size, Grid.HEIGHT * tile_size),
                )
