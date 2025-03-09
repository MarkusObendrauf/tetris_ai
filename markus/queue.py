import random
from tetraminos import ALL_TETRAMINOS, Tetramino


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
        next_piece = self._next_pieces.pop()
        self._populate_queue()
        return next_piece
