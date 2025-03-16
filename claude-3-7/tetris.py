import pygame
import random
import time
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
BOARD_WIDTH = GRID_WIDTH * GRID_SIZE
BOARD_HEIGHT = GRID_HEIGHT * GRID_SIZE
BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)      # I
BLUE = (0, 0, 255)        # J
ORANGE = (255, 165, 0)    # L
YELLOW = (255, 255, 0)    # O
GREEN = (0, 255, 0)       # S
PURPLE = (128, 0, 128)    # T
RED = (255, 0, 0)         # Z

# Timing constants (in milliseconds)
DAS = 80  # Delayed Auto Shift
ARR = 0   # Auto Repeat Rate
SOFT_DROP_RATE = 0  # Instant soft drop

# Game states
class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    COMPLETED = 3

# Tetromino definitions following Guideline
TETROMINOS = {
    'I': {'shape': [[(0, 0), (1, 0), (2, 0), (3, 0)]], 'color': CYAN},
    'J': {'shape': [[(0, 0), (0, 1), (1, 1), (2, 1)]], 'color': BLUE},
    'L': {'shape': [[(2, 0), (0, 1), (1, 1), (2, 1)]], 'color': ORANGE},
    'O': {'shape': [[(0, 0), (1, 0), (0, 1), (1, 1)]], 'color': YELLOW},
    'S': {'shape': [[(1, 0), (2, 0), (0, 1), (1, 1)]], 'color': GREEN},
    'T': {'shape': [[(1, 0), (0, 1), (1, 1), (2, 1)]], 'color': PURPLE},
    'Z': {'shape': [[(0, 0), (1, 0), (1, 1), (2, 1)]], 'color': RED}
}

# Super Rotation System (SRS) wall kick data
WALL_KICK_DATA = {
    'JLSTZ': [
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 0->1
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],    # 1->0
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],     # 1->2
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)], # 2->1
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],    # 2->3
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 3->2
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 3->0
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]     # 0->3
    ],
    'I': [
        [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],   # 0->1
        [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],   # 1->0
        [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],   # 1->2
        [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],   # 2->1
        [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],   # 2->3
        [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],   # 3->2
        [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],   # 3->0
        [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)]    # 0->3
    ],
    'O': [
        [(0, 0)], [(0, 0)], [(0, 0)], [(0, 0)],
        [(0, 0)], [(0, 0)], [(0, 0)], [(0, 0)]
    ]
}

# Generate all rotations for each tetromino
for piece in TETROMINOS:
    if piece == 'O':
        # O piece doesn't rotate
        TETROMINOS[piece]['shape'] = [TETROMINOS[piece]['shape'][0]] * 4
    else:
        # Generate rotations
        base_shape = TETROMINOS[piece]['shape'][0]
        rotations = [base_shape]

        for i in range(1, 4):
            prev_rotation = rotations[i-1]
            if piece == 'I':
                # I piece rotates around its center
                center = (1.5, 0.5) if i % 2 == 1 else (1.5, 1.5)
                new_rotation = []
                for x, y in prev_rotation:
                    rx, ry = x - center[0], y - center[1]
                    nx, ny = -ry + center[0], rx + center[1]
                    new_rotation.append((int(nx), int(ny)))
            else:
                # Other pieces rotate around (1,1)
                center = (1, 1)
                new_rotation = []
                for x, y in prev_rotation:
                    rx, ry = x - center[0], y - center[1]
                    nx, ny = -ry + center[0], rx + center[1]
                    new_rotation.append((int(nx), int(ny)))

            rotations.append(new_rotation)

        TETROMINOS[piece]['shape'] = rotations

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris 40-Line Sprint")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.state = GameState.PLAYING
        self.current_piece = None
        self.current_piece_pos = (0, 0)
        self.current_rotation = 0
        self.hold_piece = None
        self.can_hold = True
        self.next_pieces = []
        self.lines_cleared = 0
        self.start_time = time.time()
        self.end_time = None
        self.das_timer = 0
        self.das_direction = None
        self.generate_bag()
        self.spawn_piece()

    def generate_bag(self):
        # 7-bag randomizer (Guideline)
        if len(self.next_pieces) <= 7:
            bag = list(TETROMINOS.keys())
            random.shuffle(bag)
            self.next_pieces.extend(bag)

    def spawn_piece(self):
        self.generate_bag()
        self.current_piece = self.next_pieces.pop(0)
        self.current_rotation = 0

        # Set initial position (Guideline spawn position)
        if self.current_piece == 'I':
            self.current_piece_pos = (3, 0)
        elif self.current_piece == 'O':
            self.current_piece_pos = (4, 0)
        else:
            self.current_piece_pos = (3, 0)

        # Game over check
        if self.check_collision():
            self.state = GameState.GAME_OVER

        self.can_hold = True

    def hold(self):
        if not self.can_hold:
            return

        if self.hold_piece:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
            self.current_rotation = 0

            # Reset position
            if self.current_piece == 'I':
                self.current_piece_pos = (3, 0)
            elif self.current_piece == 'O':
                self.current_piece_pos = (4, 0)
            else:
                self.current_piece_pos = (3, 0)
        else:
            self.hold_piece = self.current_piece
            self.spawn_piece()

        self.can_hold = False

    def get_piece_blocks(self, piece=None, rotation=None, pos=None):
        if piece is None:
            piece = self.current_piece
        if rotation is None:
            rotation = self.current_rotation
        if pos is None:
            pos = self.current_piece_pos

        shape = TETROMINOS[piece]['shape'][rotation]
        x, y = pos
        return [(x + block_x, y + block_y) for block_x, block_y in shape]

    def check_collision(self, piece=None, rotation=None, pos=None):
        blocks = self.get_piece_blocks(piece, rotation, pos)

        for x, y in blocks:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            if y >= 0 and self.board[y][x] is not None:
                return True

        return False

    def rotate(self, direction):
        old_rotation = self.current_rotation

        # Calculate new rotation
        if direction == 1:  # Clockwise
            new_rotation = (self.current_rotation + 1) % 4
            kick_index = self.current_rotation * 2
        elif direction == -1:  # Counter-clockwise
            new_rotation = (self.current_rotation - 1) % 4
            kick_index = ((self.current_rotation - 1) % 4) * 2 + 1
        else:  # 180 rotation
            new_rotation = (self.current_rotation + 2) % 4
            # For 180 rotation, we'll try basic position first
            if not self.check_collision(rotation=new_rotation):
                self.current_rotation = new_rotation
                return True
            # Then try some basic offsets
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    new_pos = (self.current_piece_pos[0] + offset_x, self.current_piece_pos[1] + offset_y)
                    if not self.check_collision(rotation=new_rotation, pos=new_pos):
                        self.current_piece_pos = new_pos
                        self.current_rotation = new_rotation
                        return True
            return False

        # Get the appropriate wall kick data
        if self.current_piece == 'I':
            kick_data = WALL_KICK_DATA['I'][kick_index]
        elif self.current_piece == 'O':
            kick_data = WALL_KICK_DATA['O'][kick_index]
        else:
            kick_data = WALL_KICK_DATA['JLSTZ'][kick_index]

        # Try each kick offset
        for offset_x, offset_y in kick_data:
            new_pos = (self.current_piece_pos[0] + offset_x, self.current_piece_pos[1] + offset_y)
            if not self.check_collision(rotation=new_rotation, pos=new_pos):
                self.current_piece_pos = new_pos
                self.current_rotation = new_rotation
                return True

        return False

    def move(self, dx, dy):
        new_pos = (self.current_piece_pos[0] + dx, self.current_piece_pos[1] + dy)
        if not self.check_collision(pos=new_pos):
            self.current_piece_pos = new_pos
            return True
        return False

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_piece()

    def get_ghost_position(self):
        ghost_y = self.current_piece_pos[1]
        while not self.check_collision(pos=(self.current_piece_pos[0], ghost_y + 1)):
            ghost_y += 1
        return (self.current_piece_pos[0], ghost_y)

    def lock_piece(self):
        blocks = self.get_piece_blocks()
        for x, y in blocks:
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.board[y][x] = self.current_piece

        self.clear_lines()

        if self.lines_cleared >= 40:
            self.state = GameState.COMPLETED
            self.end_time = time.time()
        else:
            self.spawn_piece()

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(cell is not None for cell in self.board[y]):
                lines_to_clear.append(y)

        for y in sorted(lines_to_clear, reverse=True):
            # Remove the line
            self.board.pop(y)
            # Add a new empty line at the top
            self.board.insert(0, [None for _ in range(GRID_WIDTH)])

        self.lines_cleared += len(lines_to_clear)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state != GameState.PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
                    self.reset_game()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move(-1, 0)
                    self.das_direction = "LEFT"
                    self.das_timer = current_time
                elif event.key == pygame.K_RIGHT:
                    self.move(1, 0)
                    self.das_direction =
