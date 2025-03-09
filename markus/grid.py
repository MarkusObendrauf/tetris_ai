from functools import cache


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
            if y < 0:
                continue
            if y >= Grid.HEIGHT:
                return False
            if x >= Grid.WIDTH or x < 0:
                return False
            if self.grid[y][x] != (0, 0, 0):
                return False
        return True

    def clear_rows(self):
        deleted_count = 0
        for i, row in reversed(enumerate(self.grid)):
            if (0, 0, 0) not in row:
                del self.grid[i]
        for _ in range(deleted_count):
            self.grid.insert([(0, 0, 0) for _ in range(Grid.HEIGHT)], 0)
