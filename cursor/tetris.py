import random
import time
from enum import Enum
from typing import List, Optional, Tuple

import pygame

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
LEFT_SIDEBAR_WIDTH = 4  # Width in cells for the hold piece area
RIGHT_SIDEBAR_WIDTH = 8  # Width in cells for the next queue
SCREEN_WIDTH = CELL_SIZE * (LEFT_SIDEBAR_WIDTH + GRID_WIDTH + RIGHT_SIDEBAR_WIDTH)
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
PREVIEW_SCALE = 0.7

# Colors (Guideline colors)
COLORS = {
    "I": (0, 240, 240),  # Cyan
    "O": (240, 240, 0),  # Yellow
    "T": (160, 0, 240),  # Purple
    "S": (0, 240, 0),  # Green
    "Z": (240, 0, 0),  # Red
    "J": (0, 0, 240),  # Blue
    "L": (240, 160, 0),  # Orange
    "ghost": (128, 128, 128),
    "background": (0, 0, 0),
    "grid": (50, 50, 50),
    "text": (255, 255, 255),
}

# Tetromino shapes following Guideline
# Each piece has 4 rotations: 0 (spawn), R (right), 2 (180), L (left)
TETROMINOES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # 0
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # R
        [(0, 2), (1, 2), (2, 2), (3, 2)],  # 2
        [(1, 0), (1, 1), (1, 2), (1, 3)],  # L
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],  # All rotations are the same
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],  # 0
        [(1, 0), (1, 1), (2, 1), (1, 2)],  # R
        [(0, 1), (1, 1), (2, 1), (1, 2)],  # 2
        [(1, 0), (0, 1), (1, 1), (1, 2)],  # L
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],  # 0
        [(1, 0), (1, 1), (2, 1), (2, 2)],  # R
        [(1, 1), (2, 1), (0, 2), (1, 2)],  # 2
        [(0, 0), (0, 1), (1, 1), (1, 2)],  # L
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # 0
        [(2, 0), (1, 1), (2, 1), (1, 2)],  # R
        [(0, 1), (1, 1), (1, 2), (2, 2)],  # 2
        [(1, 0), (0, 1), (1, 1), (0, 2)],  # L
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # 0
        [(1, 0), (2, 0), (1, 1), (1, 2)],  # R
        [(0, 1), (1, 1), (2, 1), (2, 2)],  # 2
        [(1, 0), (1, 1), (0, 2), (1, 2)],  # L
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],  # 0
        [(1, 0), (1, 1), (1, 2), (2, 2)],  # R
        [(0, 1), (1, 1), (2, 1), (0, 2)],  # 2
        [(0, 0), (1, 0), (1, 1), (1, 2)],  # L
    ],
}

# SRS wall kick data
WALL_KICK_DATA = {
    "JLSTZ": [
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 0->R
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # R->0
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],  # R->2
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 2->R
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 2->L
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->2
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # L->0
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],  # 0->L
    ],
    "I": [
        [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],  # 0->R
        [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],  # R->0
        [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],  # R->2
        [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],  # 2->R
        [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],  # 2->L
        [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],  # L->2
        [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],  # L->0
        [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],  # 0->L
    ],
}


class Rotation(Enum):
    ZERO = 0
    RIGHT = 1
    TWO = 2
    LEFT = 3


class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Sprint")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_rotation = Rotation.ZERO
        self.current_pos = (0, 0)
        self.held_piece = None
        self.can_hold = True
        self.next_pieces = []
        self.bag = []
        self.lines_cleared = 0
        self.start_time = None
        self.game_over = False
        self.das_start = 0
        self.das_direction = None
        self._fill_bag()
        self.spawn_piece()

    def _fill_bag(self):
        if len(self.bag) <= 7:
            pieces = list("IJLOSTZ")
            random.shuffle(pieces)
            self.bag.extend(pieces)

    def get_next_piece(self) -> str:
        self._fill_bag()
        return self.bag.pop(0)

    def spawn_piece(self):
        if not self.next_pieces:
            self.next_pieces = [self.get_next_piece() for _ in range(5)]

        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.get_next_piece())
        self.current_rotation = Rotation.ZERO
        self.current_pos = (3, 0 if self.current_piece != "I" else -1)

        if self.check_collision():
            self.game_over = True

        if self.start_time is None:
            self.start_time = time.time()

    def get_piece_coords(
        self, piece: str, rotation: Rotation, pos: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        shape = TETROMINOES[piece][rotation.value % len(TETROMINOES[piece])]
        return [(x + pos[0], y + pos[1]) for x, y in shape]

    def check_collision(
        self, piece: str = None, rotation: Rotation = None, pos: Tuple[int, int] = None
    ) -> bool:
        piece = piece or self.current_piece
        rotation = rotation if rotation is not None else self.current_rotation
        pos = pos or self.current_pos

        coords = self.get_piece_coords(piece, rotation, pos)

        for x, y in coords:
            if not (0 <= x < GRID_WIDTH and y < GRID_HEIGHT):
                return True
            if y >= 0 and self.grid[y][x] is not None:
                return True
        return False

    def rotate_piece(self, clockwise: bool = True, one_eighty: bool = False):
        if self.current_piece == "O":
            return

        old_rotation = self.current_rotation
        if one_eighty:
            new_rotation = Rotation((old_rotation.value + 2) % 4)
        else:
            new_rotation = Rotation((old_rotation.value + (1 if clockwise else -1)) % 4)

        # Get kick data
        kick_data = WALL_KICK_DATA["I" if self.current_piece == "I" else "JLSTZ"]
        kick_tests = []

        if one_eighty:
            # For 180° rotation, try basic positions
            kick_tests = [(0, 0), (-1, 0), (1, 0), (0, 1)]
        else:
            kick_index = 2 * old_rotation.value + (1 if clockwise else 0)
            kick_tests = kick_data[kick_index]

        for dx, dy in kick_tests:
            new_pos = (self.current_pos[0] + dx, self.current_pos[1] - dy)
            if not self.check_collision(self.current_piece, new_rotation, new_pos):
                self.current_rotation = new_rotation
                self.current_pos = new_pos
                return True
        return False

    def move_piece(self, dx: int, dy: int) -> bool:
        new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
        if not self.check_collision(pos=new_pos):
            self.current_pos = new_pos
            return True
        return False

    def hard_drop(self):
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def get_ghost_position(self) -> Tuple[int, int]:
        ghost_pos = list(self.current_pos)
        while not self.check_collision(pos=(ghost_pos[0], ghost_pos[1] + 1)):
            ghost_pos[1] += 1
        return tuple(ghost_pos)

    def hold_piece(self):
        if not self.can_hold:
            return

        self.can_hold = False
        if self.held_piece is None:
            self.held_piece = self.current_piece
            self.spawn_piece()
        else:
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            self.current_rotation = Rotation.ZERO
            self.current_pos = (3, 0 if self.current_piece != "I" else -1)

    def lock_piece(self):
        coords = self.get_piece_coords(
            self.current_piece, self.current_rotation, self.current_pos
        )
        for x, y in coords:
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = self.current_piece

        self.clear_lines()
        self.can_hold = True
        self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)

        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        self.lines_cleared += len(lines_to_clear)

    def draw_grid(self):
        self.screen.fill(COLORS["background"])

        # Calculate positions
        playfield_x = LEFT_SIDEBAR_WIDTH * CELL_SIZE
        right_sidebar_x = playfield_x + GRID_WIDTH * CELL_SIZE + 20

        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                COLORS["grid"],
                (x * CELL_SIZE + playfield_x, 0),
                (x * CELL_SIZE + playfield_x, GRID_HEIGHT * CELL_SIZE),
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                COLORS["grid"],
                (playfield_x, y * CELL_SIZE),
                (playfield_x + GRID_WIDTH * CELL_SIZE, y * CELL_SIZE),
            )

        # Draw placed pieces
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        COLORS[self.grid[y][x]],
                        (
                            x * CELL_SIZE + playfield_x,
                            y * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE,
                        ),
                    )

        # Draw ghost piece
        if self.current_piece:
            ghost_pos = self.get_ghost_position()
            ghost_coords = self.get_piece_coords(
                self.current_piece, self.current_rotation, ghost_pos
            )
            for x, y in ghost_coords:
                if 0 <= y < GRID_HEIGHT:
                    pygame.draw.rect(
                        self.screen,
                        COLORS["ghost"],
                        (
                            x * CELL_SIZE + playfield_x,
                            y * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE,
                        ),
                        1,
                    )

        # Draw current piece
        if self.current_piece:
            coords = self.get_piece_coords(
                self.current_piece, self.current_rotation, self.current_pos
            )
            for x, y in coords:
                if 0 <= y < GRID_HEIGHT:
                    pygame.draw.rect(
                        self.screen,
                        COLORS[self.current_piece],
                        (
                            x * CELL_SIZE + playfield_x,
                            y * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE,
                        ),
                    )

        # Draw hold piece on the left side
        if self.held_piece:
            self.draw_piece_preview(self.held_piece, (20, 30), "HOLD")

        # Draw next pieces on the right side
        for i, piece in enumerate(self.next_pieces[:5]):
            self.draw_piece_preview(
                piece, (right_sidebar_x, 30 + i * 100), "NEXT" if i == 0 else None
            )

        # Draw lines cleared and time
        lines_text = self.font.render(
            f"Lines: {self.lines_cleared}/40", True, COLORS["text"]
        )
        self.screen.blit(lines_text, (right_sidebar_x, SCREEN_HEIGHT - 100))

        if self.start_time:
            elapsed = time.time() - self.start_time
            time_text = self.font.render(f"Time: {elapsed:.2f}", True, COLORS["text"])
            self.screen.blit(time_text, (right_sidebar_x, SCREEN_HEIGHT - 60))

        if self.lines_cleared >= 40:
            finish_time = time.time() - self.start_time
            finish_text = self.font.render(
                f"Finished! {finish_time:.2f}s", True, COLORS["text"]
            )
            self.screen.blit(finish_text, (right_sidebar_x, SCREEN_HEIGHT - 160))

    def draw_piece_preview(
        self, piece: str, pos: Tuple[int, int], label: Optional[str] = None
    ):
        if label:
            label_text = self.font.render(label, True, COLORS["text"])
            self.screen.blit(label_text, (pos[0], pos[1] - 25))

        shape = TETROMINOES[piece][0]
        min_x = min(x for x, _ in shape)
        max_x = max(x for x, _ in shape)
        min_y = min(y for _, y in shape)
        max_y = max(y for _, y in shape)
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        preview_cell_size = int(CELL_SIZE * PREVIEW_SCALE)
        offset_x = pos[0] + (4 - width) * preview_cell_size // 2
        offset_y = pos[1] + (2 - height) * preview_cell_size // 2

        for x, y in shape:
            pygame.draw.rect(
                self.screen,
                COLORS[piece],
                (
                    offset_x + x * preview_cell_size,
                    offset_y + y * preview_cell_size,
                    preview_cell_size,
                    preview_cell_size,
                ),
            )

    def run(self):
        das_time = None
        das_direction = None
        last_key_processed = None
        das_active = False  # Track if we're in DAS state

        while True:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_v:
                        self.reset_game()
                    if not self.game_over and self.lines_cleared < 40:
                        if event.key == pygame.K_UP:
                            self.rotate_piece(clockwise=True)
                        elif event.key == pygame.K_x:
                            self.rotate_piece(clockwise=False)
                        elif event.key == pygame.K_z:
                            self.rotate_piece(one_eighty=True)
                        elif event.key == pygame.K_c:
                            self.hard_drop()
                        elif event.key == pygame.K_LSHIFT:
                            self.hold_piece()
                        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            # Initial move on key press
                            dx = -1 if event.key == pygame.K_LEFT else 1
                            self.move_piece(dx, 0)
                            das_time = current_time
                            das_direction = event.key
                            last_key_processed = event.key
                            das_active = False

                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if das_direction == event.key:
                            das_time = None
                            das_direction = None
                            last_key_processed = None
                            das_active = False

            if not self.game_over and self.lines_cleared < 40:
                keys = pygame.key.get_pressed()

                # Handle DAS (Delayed Auto Shift)
                if das_direction is not None and keys[das_direction]:
                    # Check if we should activate DAS
                    if not das_active and current_time - das_time >= 0.08:  # 80ms DAS
                        das_active = True

                    # If DAS is active, keep moving to the edge
                    if das_active:
                        dx = -1 if das_direction == pygame.K_LEFT else 1
                        while self.move_piece(dx, 0):
                            pass

                elif das_time is None:
                    # Check for new key presses
                    if keys[pygame.K_LEFT] and last_key_processed != pygame.K_LEFT:
                        self.move_piece(-1, 0)
                        das_time = current_time
                        das_direction = pygame.K_LEFT
                        last_key_processed = pygame.K_LEFT
                        das_active = False
                    elif keys[pygame.K_RIGHT] and last_key_processed != pygame.K_RIGHT:
                        self.move_piece(1, 0)
                        das_time = current_time
                        das_direction = pygame.K_RIGHT
                        last_key_processed = pygame.K_RIGHT
                        das_active = False

                # Handle soft drop (instant)
                if keys[pygame.K_DOWN]:
                    self.move_piece(0, 1)

            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Tetris()
    game.run()
