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
# In the generate_bag method, modify the I piece rotation generation:
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
                # I piece rotates around its center with proper offsets
                if i == 1:  # 0->1 rotation (horizontal to vertical)
                    new_rotation = [(1, 0), (1, 1), (1, 2), (1, 3)]
                elif i == 2:  # 1->2 rotation (vertical to horizontal)
                    new_rotation = [(0, 2), (1, 2), (2, 2), (3, 2)]
                elif i == 3:  # 2->3 rotation (horizontal to vertical)
                    new_rotation = [(2, 0), (2, 1), (2, 2), (2, 3)]
                rotations.append(new_rotation)
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
        if len(self.next_pieces) <= 5:
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
                    self.das_direction = "RIGHT"
                    self.das_timer = current_time
                elif event.key == pygame.K_DOWN:
                    self.move(0, 1)
                elif event.key == pygame.K_UP:
                    self.rotate(1)  # Rotate clockwise
                elif event.key == pygame.K_x:
                    self.rotate(-1)  # Rotate counter-clockwise
                elif event.key == pygame.K_z:
                    self.rotate(2)  # Rotate 180
                elif event.key == pygame.K_c:
                    self.hard_drop()
                elif event.key == pygame.K_LSHIFT:
                    self.hold()
                elif event.key == pygame.K_v:
                    self.reset_game()

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT and self.das_direction == "LEFT") or \
                   (event.key == pygame.K_RIGHT and self.das_direction == "RIGHT"):
                    self.das_direction = None

        # Handle DAS (Delayed Auto Shift)
        if self.das_direction and current_time - self.das_timer >= DAS:
            if self.das_direction == "LEFT":
                # With ARR=0, move as far as possible in that direction
                while self.move(-1, 0):
                    pass
            elif self.das_direction == "RIGHT":
                while self.move(1, 0):
                    pass

        # Handle soft drop (instant in this case)
        if keys[pygame.K_DOWN]:
            while self.move(0, 1):
                pass

    def draw_block(self, x, y, color, alpha=255, outline=False):
        rect = pygame.Rect(
            BOARD_X + x * GRID_SIZE,
            BOARD_Y + y * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )

        if outline:
            pygame.draw.rect(self.screen, color, rect, 1)
        else:
            s = pygame.Surface((GRID_SIZE, GRID_SIZE))
            s.set_alpha(alpha)
            s.fill(color)
            self.screen.blit(s, (BOARD_X + x * GRID_SIZE, BOARD_Y + y * GRID_SIZE))
            pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_piece(self, piece, rotation, pos, alpha=255, outline=False):
        blocks = self.get_piece_blocks(piece, rotation, pos)
        color = TETROMINOS[piece]['color']

        for x, y in blocks:
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.draw_block(x, y, color, alpha, outline)

    def draw_board(self):
        # Draw background
        self.screen.fill(BLACK)

        # Draw board background
        pygame.draw.rect(self.screen, DARK_GRAY,
                         (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))

        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                            (BOARD_X + x * GRID_SIZE, BOARD_Y),
                            (BOARD_X + x * GRID_SIZE, BOARD_Y + BOARD_HEIGHT))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                            (BOARD_X, BOARD_Y + y * GRID_SIZE),
                            (BOARD_X + BOARD_WIDTH, BOARD_Y + y * GRID_SIZE))

        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    color = TETROMINOS[self.board[y][x]]['color']
                    self.draw_block(x, y, color)

        # Draw ghost piece
        if self.state == GameState.PLAYING:
            ghost_pos = self.get_ghost_position()
            self.draw_piece(self.current_piece, self.current_rotation, ghost_pos, 100, True)

        # Draw current piece
        if self.state == GameState.PLAYING:
            self.draw_piece(self.current_piece, self.current_rotation, self.current_piece_pos)

        # Draw hold piece
        hold_text = self.font.render("HOLD", True, WHITE)
        self.screen.blit(hold_text, (BOARD_X - 120, BOARD_Y + 10))

        if self.hold_piece:
            hold_x = BOARD_X - 100
            hold_y = BOARD_Y + 50

            # Center the piece in the hold box
            offset_x = 0
            offset_y = 0
            if self.hold_piece == 'I':
                offset_x = -0.5
                offset_y = 0.5
            elif self.hold_piece == 'O':
                offset_x = 0
                offset_y = 0
            else:
                offset_x = 0
                offset_y = 0

            for block_x, block_y in TETROMINOS[self.hold_piece]['shape'][0]:
                x = hold_x + (block_x + offset_x) * GRID_SIZE * 0.8
                y = hold_y + (block_y + offset_y) * GRID_SIZE * 0.8
                pygame.draw.rect(self.screen, TETROMINOS[self.hold_piece]['color'],
                                (x, y, GRID_SIZE * 0.8, GRID_SIZE * 0.8))
                pygame.draw.rect(self.screen, WHITE,
                                (x, y, GRID_SIZE * 0.8, GRID_SIZE * 0.8), 1)

        # Draw next pieces
        next_text = self.font.render("NEXT", True, WHITE)
        self.screen.blit(next_text, (BOARD_X + BOARD_WIDTH + 20, BOARD_Y + 10))

        for i, next_piece in enumerate(self.next_pieces[:5]):
            next_x = BOARD_X + BOARD_WIDTH + 40
            next_y = BOARD_Y + 50 + i * 70

            # Center the piece in the next box
            offset_x = 0
            offset_y = 0
            if next_piece == 'I':
                offset_x = -0.5
                offset_y = 0.5
            elif next_piece == 'O':
                offset_x = 0
                offset_y = 0
            else:
                offset_x = 0
                offset_y = 0

            for block_x, block_y in TETROMINOS[next_piece]['shape'][0]:
                x = next_x + (block_x + offset_x) * GRID_SIZE * 0.8
                y = next_y + (block_y + offset_y) * GRID_SIZE * 0.8
                pygame.draw.rect(self.screen, TETROMINOS[next_piece]['color'],
                                (x, y, GRID_SIZE * 0.8, GRID_SIZE * 0.8))
                pygame.draw.rect(self.screen, WHITE,
                                (x, y, GRID_SIZE * 0.8, GRID_SIZE * 0.8), 1)

        # Draw lines cleared
        lines_text = self.font.render(f"LINES: {self.lines_cleared}/40", True, WHITE)
        self.screen.blit(lines_text, (BOARD_X - 120, BOARD_Y + 200))

        # Draw time
        elapsed_time = self.end_time - self.start_time if self.end_time else time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 1000)
        time_text = self.font.render(f"TIME: {minutes:02d}:{seconds:02d}.{milliseconds:03d}", True, WHITE)
        self.screen.blit(time_text, (BOARD_X - 120, BOARD_Y + 240))

        # Draw game state messages
        if self.state == GameState.GAME_OVER:
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render("Press V to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(restart_text, restart_rect)

        elif self.state == GameState.COMPLETED:
            completed_text = self.big_font.render("40 LINES COMPLETE!", True, GREEN)
            text_rect = completed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(completed_text, text_rect)

            time_result = self.font.render(f"Time: {minutes:02d}:{seconds:02d}.{milliseconds:03d}", True, WHITE)
            time_rect = time_result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(time_result, time_rect)

            restart_text = self.font.render("Press V to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        # Draw controls
        controls_y = BOARD_Y + BOARD_HEIGHT - 200
        controls_text = [
            "CONTROLS:",
            "Left/Right: Move",
            "Down: Soft Drop",
            "C: Hard Drop",
            "Up: Rotate Right",
            "X: Rotate Left",
            "Z: Rotate 180°",
            "Shift: Hold",
            "V: Reset Game"
        ]

        for i, text in enumerate(controls_text):
            control_text = self.font.render(text, True, WHITE)
            self.screen.blit(control_text, (BOARD_X + BOARD_WIDTH + 20, controls_y + i * 30))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.draw_board()
            self.clock.tick(60)

# Create and run the game
if __name__ == "__main__":
    game = Tetris()
    game.run()
