import pygame
import random

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 640, 480
BLOCK_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = 10, 20
DAS = 80  # Delayed Auto Shift
ARR = 0  # Auto Repeat Rate
SOFT_DROP = 1  # Instant soft drop

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Define piece shapes
PIECES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

# Define piece rotations
ROTATIONS = {
    'I': [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    'J': [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],
    'L': [[[0, 0, 1], [1, 1, 1]], [[1, 1], [0, 1], [0, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 0], [1, 0], [1, 1]]],
    'O': [[[1, 1], [1, 1]], [[1, 1], [1, 1]], [[1, 1], [1, 1]], [[1, 1], [1, 1]]],
    'S': [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]], [[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],
    'T': [[[0, 1, 0], [1, 1, 1]], [[1, 1], [0, 1], [0, 1]], [[1, 1, 1], [0, 1, 0]], [[1, 0], [1, 1], [1, 0]]],
    'Z': [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]], [[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]
}

# Define game class
class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece = None
        self.piece_x, self.piece_y = 0, 0
        self.piece_rotation = 0
        self.hold_piece = None
        self.next_pieces = [random.choice(list(PIECES.keys())) for _ in range(5)]
        self.score = 0
        self.lines = 0
        self.time = 0
        self.das_timer = 0

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1)
                    elif event.key == pygame.K_DOWN:
                        self.soft_drop()
                    elif event.key == pygame.K_c:
                        self.hard_drop()
                    elif event.key == pygame.K_x:
                        self.rotate_piece(-1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece(1)
                    elif event.key == pygame.K_z:
                        self.rotate_piece(2)
                    elif event.key == pygame.K_SHIFT:
                        self.hold_piece()
                    elif event.key == pygame.K_v:
                        self.reset_game()

            self.update()
            self.draw()

        pygame.quit()

    def update(self):
        self.time += 1 / 60
        self.das_timer += 1
        if self.das_timer >= DAS:
            self.das_timer = 0
            self.move_piece(0)

        if self.piece is None:
            self.spawn_piece()

        if self.piece:
            self.check_collision()

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_grid()
        self.draw_piece()
        self.draw_ghost_piece()
        self.draw_hold_piece()
        self.draw_next_pieces()
        self.draw_score()
        self.draw_time()
        pygame.display.flip()

    def spawn_piece(self):
        self.piece = self.next_pieces.pop(0)
        self.next_pieces.append(random.choice(list(PIECES.keys())))
        self.piece_x, self.piece_y = GRID_WIDTH // 2, 0
        self.piece_rotation = 0

    def move_piece(self, dx):
        self.piece_x += dx
        if self.check_collision():
            self.piece_x -= dx

    def soft_drop(self):
        self.piece_y += 1
        if self.check_collision():
            self.piece_y -= 1
            self.lock_piece()

    def hard_drop(self):
        while not self.check_collision():
            self.piece_y += 1
        self.piece_y -= 1
        self.lock_piece()

    def rotate_piece(self, dr):
        self.piece_rotation += dr
        if self.piece_rotation >= 4:
            self.piece_rotation = 0
        elif self.piece_rotation < 0:
            self.piece_rotation = 3
        if self.check_collision():
            self.piece_rotation -= dr
            if self.piece_rotation < 0:
                self.piece_rotation = 3

    def hold_piece(self):
        if self.hold_piece is None:
            self.hold_piece = self.piece
            self.spawn_piece()
        else:
            self.piece, self.hold_piece = self.hold_piece, self.piece

    def check_collision(self):
        piece_shape = ROTATIONS[self.piece][self.piece_rotation]
        for y, row in enumerate(piece_shape):
            for x, val in enumerate(row):
                if val and (self.piece_x + x < 0 or self.piece_x + x >= GRID_WIDTH or
                            self.piece_y + y < 0 or self.piece_y + y >= GRID_HEIGHT or
                            self.grid[self.piece_y + y][self.piece_x + x]):
                    return True
        return False

    def lock_piece(self):
        piece_shape = ROTATIONS[self.piece][self.piece_rotation]
        for y, row in enumerate(piece_shape):
            for x, val in enumerate(row):
                if val:
                    self.grid[self.piece_y + y][self.piece_x + x] = 1
        self.clear_lines()
        self.piece = None

    def clear_lines(self):
        lines_cleared = 0
        for y, row in enumerate(self.grid):
            if all(row):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        self.lines += lines_cleared
        if self.lines >= 40:
            print(f"Time: {self.time:.2f} seconds")

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, GRAY, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self):
        piece_shape = ROTATIONS[self.piece][self.piece_rotation]
        for y, row in enumerate(piece_shape):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, WHITE, ((self.piece_x + x) * BLOCK_SIZE, (self.piece_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_ghost_piece(self):
        piece_shape = ROTATIONS[self.piece][self.piece_rotation]
        ghost_y = self.piece_y
        while ghost_y + len(piece_shape) < GRID_HEIGHT and not self.check_collision_ghost(ghost_y + 1):
            ghost_y += 1
        for y, row in enumerate(piece_shape):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, GRAY, ((self.piece_x + x) * BLOCK_SIZE, (ghost_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def check_collision_ghost(self, dy):
        piece_shape = ROTATIONS[self.piece][self.piece_rotation]
        for y, row in enumerate(piece_shape):
            for x, val in enumerate(row):
                if val and (self.piece_x + x < 0 or self.piece_x + x >= GRID_WIDTH or
                            self.piece_y + dy + y < 0 or self.piece_y + dy + y >= GRID_HEIGHT or
                            self.grid[self.piece_y + dy + y][self.piece_x + x]):
                    return True
        return False

    def draw_hold_piece(self):
        if self.hold_piece:
            piece_shape = PIECES[self.hold_piece]
            for y, row in enumerate(piece_shape):
                for x, val in enumerate(row):
                    if val:
                        pygame.draw.rect(self.screen, WHITE, ((x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_next_pieces(self):
        for i, piece in enumerate(self.next_pieces):
            piece_shape = PIECES[piece]
            for y, row in enumerate(piece_shape):
                for x, val in enumerate(row):
                    if val:
                        pygame.draw.rect(self.screen, WHITE, ((x + 1) * BLOCK_SIZE, (y + 1 + i * 5) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_score(self):
        text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(text, (10, 10))

    def draw_time(self):
        text = self.font.render(f"Time: {self.time:.2f}", True, WHITE)
        self.screen.blit(text, (10, 50))

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece = None
        self.piece_x, self.piece_y = 0, 0
        self.piece_rotation = 0
        self.hold_piece = None
        self.next_pieces = [random.choice(list(PIECES.keys())) for _ in range(5)]
        self.score = 0
        self.lines = 0
        self.time = 0

if __name__ == "__main__":
    game = Tetris()
    game.run()
