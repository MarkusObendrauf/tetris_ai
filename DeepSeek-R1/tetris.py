import pygame
import random
import time

# Initialize Pygame
pygame.init()
pygame.display.set_caption("40-Line Sprint")

# Game constants
CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
VISIBLE_HEIGHT = 20
WIDTH = CELL_SIZE * (10 + 6 + 6)
HEIGHT = CELL_SIZE * VISIBLE_HEIGHT
FPS = 60
DAS_DELAY = 80  # 80ms before autorepeat starts
SOFT_DROP_SPEED = 1  # Instant movement

# Enhanced SRS data with proper wall kicks
I_WALL_KICKS = [
    [[(-2, 0), (1, 0), (-2, -1), (1, 2)], [(-1, 0), (2, 0), (-1, 2), (2, -1)]],
    [[(-1, 0), (2, 0), (-1, -2), (2, 1)], [(2, 0), (-1, 0), (2, -1), (-1, 2)]],
    [[(2, 0), (-1, 0), (2, 1), (-1, -2)], [(1, 0), (-2, 0), (1, 2), (-2, -1)]],
    [[(1, 0), (-2, 0), (1, -2), (-2, 1)], [(-2, 0), (1, 0), (-2, 1), (1, -2)]]
]

JLSTZ_WALL_KICKS = [
    [[(-1, 0), (-1, 1), (0, -2), (-1, -2)], [(1, 0), (1, 1), (0, -2), (1, -2)]],
    [[(1, 0), (1, -1), (0, 2), (1, 2)], [(-1, 0), (-1, -1), (0, 2), (-1, 2)]],
    [[(1, 0), (1, 1), (0, -2), (1, -2)], [(-1, 0), (-1, 1), (0, -2), (-1, -2)]],
    [[(-1, 0), (-1, -1), (0, 2), (-1, 2)], [(1, 0), (1, -1), (0, 2), (1, 2)]]
]


# Colors (Tetris Guideline)
COLORS = [
    (0, 0, 0),        # 0: Black (empty)
    (0, 240, 240),    # 1: I cyan
    (240, 240, 0),    # 2: O yellow
    (160, 0, 240),    # 3: T purple
    (240, 160, 0),    # 4: L orange
    (0, 0, 240),      # 5: J blue
    (0, 240, 0),      # 6: S green
    (240, 0, 0),      # 7: Z red
    (128, 128, 128)   # 8: Ghost gray
]

# SRS piece data and wall kicks
TETRIMINOS = {
    'I': {
        'shape': [[1, 1, 1, 1]],
        'color': 1,
        'wall_kicks': [
            [(-2, 0), (1, 0), (-2, -1), (1, 2)],
            [(-1, 0), (2, 0), (-1, 2), (2, -1)],
            [(2, 0), (-1, 0), (2, 1), (-1, -2)],
            [(-2, 0), (1, 0), (-2, 1), (1, -2)]
        ]
    },
    'O': {
        'shape': [[1, 1], [1, 1]],
        'color': 2,
        'wall_kicks': [[(0, 0)] for _ in range(4)]
    },
    'T': {
        'shape': [[0, 1, 0], [1, 1, 1]],
        'color': 3,
        'wall_kicks': [
            [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(1, 0), (1, -1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (0, -2), (1, -2)],
            [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
    },
    'L': {
        'shape': [[0, 0, 1], [1, 1, 1]],
        'color': 4,
        'wall_kicks': [
            [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(1, 0), (1, -1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (0, -2), (1, -2)],
            [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
    },
    'J': {
        'shape': [[1, 0, 0], [1, 1, 1]],
        'color': 5,
        'wall_kicks': [
            [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(1, 0), (1, -1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (0, -2), (1, -2)],
            [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
    },
    'S': {
        'shape': [[0, 1, 1], [1, 1, 0]],
        'color': 6,
        'wall_kicks': [
            [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(1, 0), (1, -1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (0, -2), (1, -2)],
            [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
    },
    'Z': {
        'shape': [[1, 1, 0], [0, 1, 1]],
        'color': 7,
        'wall_kicks': [
            [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
            [(1, 0), (1, -1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (0, -2), (1, -2)],
            [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]
    }
}

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.bag = []
        self.hold_piece = None
        self.can_hold = True
        self.current_piece = None
        self.next_pieces = []
        self.ghost_piece = None
        self.das_timer = {'left': 0, 'right': 0}
        self.game_start_time = time.time()
        self.last_update = time.time()
        self.game_over = False
        self._fill_bag()
        self._spawn_new_piece()

    def _fill_bag(self):
        # Keep adding complete 7-bags until we have enough pieces
        while len(self.next_pieces) < 5:
            if not self.bag:
                # Create new 7-bag when empty
                self.bag = list(TETRIMINOS.keys())
                random.shuffle(self.bag)
            # Take only as many as needed from current bag
            needed = 5 - len(self.next_pieces)
            take = min(needed, len(self.bag))
            self.next_pieces.extend(self.bag[:take])
            self.bag = self.bag[take:]

    def _spawn_new_piece(self):
        if not self.next_pieces:
            self._fill_bag()

        # Always keep 5 pieces in the queue
        if len(self.next_pieces) <= 5:
            self._fill_bag()

        piece_type = self.next_pieces.pop(0)
        self.current_piece = {
            'type': piece_type,
            'shape': TETRIMINOS[piece_type]['shape'],
            'color': TETRIMINOS[piece_type]['color'],
            'x': BOARD_WIDTH // 2 - 2,
            'y': 0,
            'rotation': 0
        }
        self.can_hold = True
        self.ghost_piece = self._get_ghost_position()

        if self._check_collision():
            self.game_over = True


    def _get_ghost_position(self):
        ghost = self.current_piece.copy()
        while not self._check_collision(ghost):
            ghost['y'] += 1
        ghost['y'] -= 1
        return ghost

    def _check_collision(self, piece=None):
        piece = piece or self.current_piece
        shape = self._get_rotated_shape(piece)
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = piece['x'] + x
                    py = piece['y'] + y
                    if px < 0 or px >= BOARD_WIDTH or py >= BOARD_HEIGHT:
                        return True
                    if py >= 0 and self.board[py][px]:
                        return True
        return False

    def _get_rotated_shape(self, piece):
        shape = piece['shape']
        for _ in range(piece['rotation'] % 4):
            shape = list(zip(*shape[::-1]))
        return shape

    def _rotate_piece(self, direction):
        original_rotation = self.current_piece['rotation']
        self.current_piece['rotation'] = (self.current_piece['rotation'] + direction) % 4
        kicks = TETRIMINOS[self.current_piece['type']]['wall_kicks'][original_rotation]

        for kick in kicks:
            self.current_piece['x'] += kick[0]
            self.current_piece['y'] -= kick[1]
            if not self._check_collision():
                self.ghost_piece = self._get_ghost_position()
                return
            self.current_piece['x'] -= kick[0]
            self.current_piece['y'] += kick[1]

        self.current_piece['rotation'] = original_rotation

    def _lock_piece(self):
        shape = self._get_rotated_shape(self.current_piece)
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece['x'] + x
                    py = self.current_piece['y'] + y
                    if py >= 0:
                        self.board[py][px] = self.current_piece['color']

        lines_cleared = 0
        full_lines = []
        for y in range(BOARD_HEIGHT):
            if all(self.board[y]):
                full_lines.append(y)

        for y in full_lines:
            del self.board[y]
            self.board.insert(0, [0] * BOARD_WIDTH)
            lines_cleared += 1

        self.lines += lines_cleared
        if self.lines >= 40:
            self.game_over = True
            return

        self._spawn_new_piece()

    def _hold_piece(self):
        if not self.can_hold:
            return
        if self.hold_piece:
            self.current_piece, self.hold_piece = self.hold_piece, self.current_piece
            self.current_piece['x'] = BOARD_WIDTH // 2 - 2
            self.current_piece['y'] = 0
            self.current_piece['rotation'] = 0
        else:
            self.hold_piece = self.current_piece
            self._spawn_new_piece()
        self.can_hold = False
        self.ghost_piece = self._get_ghost_position()

    def _handle_input(self):
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.reset_game()
                if self.game_over:
                    continue

                # Immediate movement on key press
                if event.key == pygame.K_LEFT:
                    self._move(-1)
                    self.das_timer['left'] = now
                elif event.key == pygame.K_RIGHT:
                    self._move(1)
                    self.das_timer['right'] = now
                elif event.key == pygame.K_UP:
                    self._rotate(1)
                elif event.key == pygame.K_x:
                    self._rotate(-1)
                elif event.key == pygame.K_z:
                    self._rotate(2)
                elif event.key == pygame.K_LSHIFT:
                    self._hold_piece()
                elif event.key == pygame.K_c:
                    self._hard_drop()

        # DAS handling with initial move
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and now - self.das_timer['left'] > DAS_DELAY/1000:
            self._move(-1)
        if keys[pygame.K_RIGHT] and now - self.das_timer['right'] > DAS_DELAY/1000:
            self._move(1)


    def _rotate(self, direction):
        original = self.current_piece.copy()
        kicks = self._get_kick_table(original['rotation'], direction)

        self.current_piece['rotation'] = (original['rotation'] + direction) % 4

        for kick in kicks:
            self.current_piece['x'] = original['x'] + kick[0]
            self.current_piece['y'] = original['y'] - kick[1]

            if not self._check_collision():
                self.ghost_piece = self._get_ghost_position()
                return

        # Rotation failed - revert
        self.current_piece = original

    def _get_kick_table(self, current_rotation, direction):
        piece_type = self.current_piece['type']
        if piece_type == 'I':
            return I_WALL_KICKS[current_rotation][direction > 0]
        elif piece_type == 'O':
            return [(0, 0)]
        else:
            return JLSTZ_WALL_KICKS[current_rotation][direction > 0]


    def _move(self, dx):
        self.current_piece['x'] += dx
        if self._check_collision():
            self.current_piece['x'] -= dx
        else:
            self.ghost_piece = self._get_ghost_position()

    def _soft_drop(self):
        self.current_piece['y'] += 1
        if self._check_collision():
            self.current_piece['y'] -= 1
            self._lock_piece()
        else:
            self.score += 1
        self.ghost_piece = self._get_ghost_position()

    def _hard_drop(self):
        while not self._check_collision():
            self.current_piece['y'] += 1
            self.score += 2
        self.current_piece['y'] -= 1
        self._lock_piece()

    def _draw_matrix(self, matrix, offset, color, ghost=False):
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    col = COLORS[8] if ghost else COLORS[color]
                    pygame.draw.rect(
                        self.screen,
                        col,
                        (
                            (offset[0] + x) * CELL_SIZE + 1,
                            (offset[1] + y) * CELL_SIZE + 1,
                            CELL_SIZE - 2,
                            CELL_SIZE - 2
                        )
                    )

    # Modified drawing calls for proper colors:
    def _draw(self):
        self.screen.fill((0, 0, 0))

        # Draw game board
        for y in range(VISIBLE_HEIGHT):
            for x in range(BOARD_WIDTH):
                val = self.board[y][x] if y >= 0 else 0
                pygame.draw.rect(
                    self.screen,
                    COLORS[val],
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                )

        # Draw current piece with proper color
        if self.current_piece:
            shape = self._get_rotated_shape(self.current_piece)
            self._draw_matrix(shape,
                            (self.current_piece['x'], self.current_piece['y']),
                            self.current_piece['color'])

        # Draw ghost piece
        if self.ghost_piece:
            ghost_shape = self._get_rotated_shape(self.ghost_piece)
            self._draw_matrix(ghost_shape,
                            (self.ghost_piece['x'], self.ghost_piece['y']),
                            self.ghost_piece['color'],
                            ghost=True)

        # Draw next pieces with proper colors
        next_x = BOARD_WIDTH + 2
        for i, piece_type in enumerate(self.next_pieces[:5]):
            piece = TETRIMINOS[piece_type]
            self._draw_matrix(piece['shape'], (next_x, 2 + i * 3), piece['color'])

        # Draw hold piece
        if self.hold_piece:
            self._draw_matrix(self.hold_piece['shape'], (-6, 2), self.hold_piece['color'])

        # UI elements remain the same
        pygame.display.update()

    def run(self):
        while True:
            self._handle_input()
            if not self.game_over:
                self._draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
