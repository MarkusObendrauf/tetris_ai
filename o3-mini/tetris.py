#!/usr/bin/env python3
"""
Tetris 40-line Sprint

Controls:
   Move Left:       left arrow
   Move Right:      right arrow
   Soft Drop:       down arrow (instant move down)
   Hard Drop:       c
   Rotate Left:     up      (counterclockwise)
   Rotate Right:    x       (clockwise)
   Rotate 180:      z   (no wall kicks on 180)
   Hold:            shift
   Reset game:      v

Movement settings:
   DAS = 80ms; ARR = instant (after DAS, the piece zooms to the far side).
   Soft drop is instant.
"""

import pygame, random, sys

# Pygame initialization
pygame.init()
WIDTH, HEIGHT = 400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris 40line Sprint")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)

# Board configuration
COLS, ROWS = 10, 22  # top two rows hidden
CELL_SIZE = 32
BOARD_TOP = 60

# Colors for pieces and grid
COLORS = {
    "I": (0, 240, 240),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
    "O": (240, 240, 0),
    "S": (0, 240, 0),
    "T": (160, 0, 240),
    "Z": (240, 0, 0),
    "grid": (40, 40, 40),
    "bg": (10, 10, 10),
    "ghost": (100,100,100)
}

# Tetromino definitions using offsets for each rotation (0,1,2,3)
PIECES = {
    "I": [
        [(-1,0),(0,0),(1,0),(2,0)],
        [(1,-1),(1,0),(1,1),(1,2)],
        [(-1,1),(0,1),(1,1),(2,1)],
        [(0,-1),(0,0),(0,1),(0,2)]
    ],
    "J": [
        [(-1,0),(0,0),(1,0),(-1,1)],
        [(0,-1),(0,0),(0,1),(1,-1)],
        [(-1,0),(0,0),(1,0),(1,-1)],
        [(0,-1),(0,0),(0,1),(-1,1)]
    ],
    "L": [
        [(-1,0),(0,0),(1,0),(1,1)],
        [(0,-1),(0,0),(0,1),(1,1)],
        [(-1,0),(0,0),(1,0),(-1,-1)],
        [(0,-1),(0,0),(0,1),(-1,-1)]
    ],
    "O": [
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)],
        [(0,0),(1,0),(0,1),(1,1)]
    ],
    "S": [
        [(0,0),(1,0),(-1,1),(0,1)],
        [(0,-1),(0,0),(1,0),(1,1)],
        [(0,0),(1,0),(-1,1),(0,1)],
        [(0,-1),(0,0),(1,0),(1,1)]
    ],
    "T": [
        [(-1,0),(0,0),(1,0),(0,1)],
        [(0,-1),(0,0),(0,1),(1,0)],
        [(-1,0),(0,0),(1,0),(0,-1)],
        [(0,-1),(0,0),(0,1),(-1,0)]
    ],
    "Z": [
        [(-1,0),(0,0),(0,1),(1,1)],
        [(1,-1),(0,0),(1,0),(0,1)],
        [(-1,0),(0,0),(0,1),(1,1)],
        [(1,-1),(0,0),(1,0),(0,1)]
    ]
}

# SRS wall kick tables (simplified) for non-I and I pieces.
WALL_KICKS = {
    "normal": {
        "CW": [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
        "CCW": [(0,0), (1,0), (1,-1), (0,2), (1,2)]
    },
    "I": {
        "CW": [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
        "CCW": [(0,0), (2,0), (-1,0), (2,1), (-1,-2)]
    }
}

def create_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def draw_board(board):
    for y in range(2, ROWS):  # skip hidden top two rows
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, BOARD_TOP + (y-2)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, COLORS["grid"], rect, 1)
            if board[y][x]:
                pygame.draw.rect(screen, COLORS[board[y][x]], rect.inflate(-2, -2))

def clear_lines(board):
    cleared = 0
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [None for _ in range(COLS)])
    return new_board, cleared

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rotation = 0
        # Spawn location: center horizontally; allow above-board spawn with y=-2.
        self.x = 3
        self.y = -2

    def get_blocks(self, rotation=None, pos=None):
        rot = self.rotation if rotation is None else rotation
        px = self.x if pos is None else pos[0]
        py = self.y if pos is None else pos[1]
        return [(px + dx, py + dy) for dx,dy in PIECES[self.shape][rot]]

    def rotate(self, direction, board):
        # direction: "CW" for clockwise, "CCW" for counterclockwise.
        if self.shape == "O":
            return True  # The O-piece does not change.
        old_rotation = self.rotation
        new_rotation = (self.rotation + (1 if direction=="CW" else -1)) % 4
        offsets = (WALL_KICKS["I"] if self.shape=="I" else WALL_KICKS["normal"])[direction]
        for ox, oy in offsets:
            new_x = self.x + ox
            new_y = self.y + oy
            new_blocks = [(new_x + dx, new_y + dy) for dx,dy in PIECES[self.shape][new_rotation]]
            if valid_position(new_blocks, board):
                self.rotation = new_rotation
                self.x = new_x
                self.y = new_y
                return True
        return False

    def rotate180(self, board):
        if self.shape == "O":
            return True
        new_rotation = (self.rotation + 2) % 4
        new_blocks = [(self.x + dx, self.y + dy) for dx,dy in PIECES[self.shape][new_rotation]]
        if valid_position(new_blocks, board):
            self.rotation = new_rotation
            return True
        return False

def valid_position(blocks, board):
    for x, y in blocks:
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and board[y][x]:
            return False
    return True

def get_ghost(piece, board):
    ghost = Piece(piece.shape)
    ghost.rotation = piece.rotation
    ghost.x = piece.x
    ghost.y = piece.y
    while True:
        next_blocks = ghost.get_blocks(pos=(ghost.x, ghost.y+1))
        if valid_position(next_blocks, board):
            ghost.y += 1
        else:
            break
    return ghost

# Slide the piece horizontally all the way until it cannot move further.
def slide_piece(piece, board, dx):
    candidate = piece.x
    while True:
        new_blocks = [(candidate + dx + bx, piece.y + by) for bx,by in PIECES[piece.shape][piece.rotation]]
        if valid_position(new_blocks, board):
            candidate += dx
        else:
            break
    piece.x = candidate

class Bag:
    def __init__(self):
        self.bag = []
        self.fill_bag()

    def fill_bag(self):
        self.bag = list(PIECES.keys())
        random.shuffle(self.bag)

    def next(self):
        if not self.bag:
            self.fill_bag()
        return self.bag.pop()

class TetrisGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = create_board()
        self.bag = Bag()
        self.next_queue = [self.bag.next() for _ in range(5)]
        self.current = Piece(self.bag.next())
        self.hold = None
        self.can_hold = True
        self.gravity_timer = 0
        self.total_cleared = 0
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        self.finish_time = None
        # For DAS/ARR handling.
        self.left_pressed = False
        self.right_pressed = False
        self.left_timer = 0
        self.right_timer = 0

    def spawn_piece(self):
        self.current = Piece(self.next_queue.pop(0))
        self.next_queue.append(self.bag.next())
        self.can_hold = True
        if not valid_position(self.current.get_blocks(), self.board):
            self.game_over = True

    def hold_piece(self):
        if not self.can_hold:
            return
        self.can_hold = False
        if self.hold is None:
            self.hold = self.current.shape
            self.spawn_piece()
        else:
            self.current, self.hold = Piece(self.hold), self.current.shape
            self.current.x = 3
            self.current.y = -2

    def hard_drop(self):
        ghost = get_ghost(self.current, self.board)
        self.current.y = ghost.y
        self.lock_piece()

    def lock_piece(self):
        for x, y in self.current.get_blocks():
            if y >= 0:
                self.board[y][x] = self.current.shape
        self.board, cleared = clear_lines(self.board)
        self.total_cleared += cleared
        if self.total_cleared >= 40 and self.finish_time is None:
            self.finish_time = pygame.time.get_ticks() - self.start_time
        self.spawn_piece()

    def move(self, dx, dy):
        new_x = self.current.x + dx
        new_y = self.current.y + dy
        new_blocks = [(new_x + bx, new_y + by) for bx,by in PIECES[self.current.shape][self.current.rotation]]
        if valid_position(new_blocks, self.board):
            self.current.x = new_x
            self.current.y = new_y
            return True
        return False

    def update(self, dt):
        if self.game_over or (self.finish_time is not None):
            return

        self.gravity_timer += dt
        # Gravity drop: for sprint mode use a long drop delay since players will hard drop.
        drop_interval = 1000  # ms
        if self.gravity_timer >= drop_interval:
            if not self.move(0, 1):
                self.lock_piece()
            self.gravity_timer = 0

        now = pygame.time.get_ticks()
        # DAS / Instant ARR: once the DAS delay (80ms) is exceeded,
        # the piece instantly moves hard in that direction (as far as it can go).
        if self.left_pressed:
            if self.left_timer == 0:
                self.left_timer = now
            if now - self.left_timer >= 80:
                slide_piece(self.current, self.board, -1)
                self.left_timer = now  # reset timer so key release is required to re-trigger
        else:
            self.left_timer = 0

        if self.right_pressed:
            if self.right_timer == 0:
                self.right_timer = now
            if now - self.right_timer >= 80:
                slide_piece(self.current, self.board, 1)
                self.right_timer = now
        else:
            self.right_timer = 0

    def draw(self):
        screen.fill(COLORS["bg"])
        draw_board(self.board)

        # Draw ghost piece.
        ghost = get_ghost(self.current, self.board)
        for x, y in ghost.get_blocks():
            if y >= 2:
                rect = pygame.Rect(x * CELL_SIZE, BOARD_TOP + (y-2)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, COLORS["ghost"], rect, 1)

        # Draw current piece.
        for x, y in self.current.get_blocks():
            if y >= 2:
                rect = pygame.Rect(x * CELL_SIZE, BOARD_TOP + (y-2)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, COLORS[self.current.shape], rect.inflate(-2, -2))

        # Draw hold area.
        hold_text = FONT.render("Hold", True, (200,200,200))
        screen.blit(hold_text, (COLS * CELL_SIZE + 20, 60))
        if self.hold:
            for dx, dy in PIECES[self.hold][0]:
                rect = pygame.Rect(COLS * CELL_SIZE + 20 + (dx+1)*CELL_SIZE//2,
                                   90 + (dy+1)*CELL_SIZE//2, CELL_SIZE//2, CELL_SIZE//2)
                pygame.draw.rect(screen, COLORS[self.hold], rect.inflate(-2, -2))

        # Draw next queue area.
        next_text = FONT.render("Next", True, (200,200,200))
        screen.blit(next_text, (COLS * CELL_SIZE + 20, 200))
        for i, shape in enumerate(self.next_queue):
            for dx, dy in PIECES[shape][0]:
                rect = pygame.Rect(COLS * CELL_SIZE + 20 + (dx+1)*CELL_SIZE//2,
                                   230 + i*CELL_SIZE + (dy+1)*CELL_SIZE//2, CELL_SIZE//2, CELL_SIZE//2)
                pygame.draw.rect(screen, COLORS[shape], rect.inflate(-2, -2))

        # Display finish time if 40 lines have been cleared.
        if self.finish_time is not None:
            t_sec = self.finish_time / 1000.0
            time_text = FONT.render(f"Time: {t_sec:.2f}s", True, (255,255,255))
            screen.blit(time_text, (20, 20))
        pygame.display.flip()

game = TetrisGame()

# Main game loop.
while True:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Reset game.
            if event.key == pygame.K_v:
                game.reset()
            # Do not process further if game over or sprint complete.
            if game.game_over or game.finish_time is not None:
                continue
            # Note: Per the updated mapping:
            #   Up arrow rotates left (counterclockwise).
            #   x rotates right (clockwise).
            if event.key == pygame.K_UP:
                game.current.rotate("CCW", game.board)
            elif event.key == pygame.K_x:
                game.current.rotate("CW", game.board)
            elif event.key == pygame.K_z:
                game.current.rotate180(game.board)
            elif event.key == pygame.K_DOWN:
                if not game.move(0, 1):
                    game.lock_piece()
            elif event.key == pygame.K_c:
                game.hard_drop()
            elif event.key in (pygame.K_RSHIFT, pygame.K_LSHIFT):
                game.hold_piece()
            elif event.key == pygame.K_LEFT:
                game.left_pressed = True
            elif event.key == pygame.K_RIGHT:
                game.right_pressed = True

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                game.left_pressed = False
            elif event.key == pygame.K_RIGHT:
                game.right_pressed = False

    game.update(dt)
    game.draw()

