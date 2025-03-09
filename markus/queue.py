import random

import pygame
from active_tetramino import ActiveTetramino
from tetraminos import ALL_TETRAMINOS, Tetramino


VISIBLE_QUEUE_LENGTH = 5
QUEUE_PIECE_HEIGHT = 3


class Queue:
    def __init__(self):
        self._next_pieces = []
        self._populate_queue()

    def _populate_queue(self):
        while len(self._next_pieces) < 100:
            self._add_bag()

    def _add_bag(self):
        random.shuffle(ALL_TETRAMINOS)
        self._next_pieces += ALL_TETRAMINOS

    def pop(self) -> Tetramino:
        next_piece = self._next_pieces.pop(0)
        self._populate_queue()
        return next_piece

    def peek(self) -> Tetramino:
        return self._next_pieces[0]

    def draw(self, surface: pygame.Surface, tile_size: int):
        for i, piece in enumerate(self._next_pieces[:VISIBLE_QUEUE_LENGTH]):
            y_offset = tile_size * (i * QUEUE_PIECE_HEIGHT + 1)
            x_offset = -3 * tile_size
            for x, y in ActiveTetramino(piece).get_positions():
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (
                        x * tile_size + x_offset,
                        y * tile_size + y_offset,
                        tile_size,
                        tile_size,
                    ),
                    0,
                )
