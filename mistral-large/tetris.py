import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
GRID_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE

# Colors according to the Tetris Guideline
COLORS = [
    (0, 0, 0),        # Empty
    (0, 255, 255),    # I
    (0, 0, 255),      # J
    (255, 165, 0),    # L
    (255, 255, 0),    # O
    (0, 255, 0),      # S
    (128, 0, 128),    # T
    (255, 0, 0)       # Z
]

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1, 1]],   # I
    [[2, 0, 0], [2, 2, 2]],  # J
    [[0, 0, 3], [3, 3, 3]],  # L
    [[4, 4], [4, 4]],  # O
    [[0, 5, 5], [5, 5, 0]],  # S
    [[6, 6, 6], [0, 6, 0]],  # T
    [[7, 7, 0], [0, 7, 7]]   # Z
]

# Tetris Guideline randomizer
def generate_bag():
    bag = list(range(len(SHAPES)))
    random.shuffle(bag)
    return bag

# Game variables
grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
current_piece = None
next_pieces = []
held_piece = None
hold_used = False
score = 0
lines_cleared = 0
start_time = time.time()
game_over = False
das_timer = 0
das_delay = 80  # DAS delay in milliseconds

# Initialize next pieces queue
next_pieces = generate_bag() + generate_bag()

# Function to create a new piece
def new_piece():
    global current_piece, next_pieces, hold_used
    if not next_pieces:
        next_pieces = generate_bag()
    shape = next_pieces.pop(0)
    current_piece = {'shape': SHAPES[shape], 'color': shape + 1, 'x': GRID_WIDTH // 2 - 2, 'y': 0}
    hold_used = False

# Function to check collision
def check_collision(shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and (x + off_x < 0 or x + off_x >= GRID_WIDTH or y + off_y >= GRID_HEIGHT or grid[y + off_y][x + off_x]):
                return True
    return False

# Function to join piece to the grid
def join_piece():
    global current_piece, score, lines_cleared
    shape = current_piece['shape']
    off_x, off_y = current_piece['x'], current_piece['y']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + off_y][x + off_x] = current_piece['color']
    clear_lines()
    new_piece()
    if check_collision(current_piece['shape'], (current_piece['x'], current_piece['y'])):
        game_over = True

# Function to clear lines
def clear_lines():
    global score, lines_cleared
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared_lines = GRID_HEIGHT - len(new_grid)
    lines_cleared += cleared_lines
    score += cleared_lines
    grid[:len(new_grid)] = new_grid
    grid[len(new_grid):] = [[0] * GRID_WIDTH for _ in range(cleared_lines)]

# Function to rotate piece
def rotate_piece(shape, clockwise=True):
    return [list(row) for row in zip(*shape[::-1])] if clockwise else [list(row) for row in zip(*shape)][::-1]

# Function to handle piece movement
def move_piece(dx, dy):
    current_piece['x'] += dx
    current_piece['y'] += dy
    if check_collision(current_piece['shape'], (current_piece['x'], current_piece['y'])):
        current_piece['x'] -= dx
        current_piece['y'] -= dy
        return False
    return True

# Function to handle piece rotation
def rotate_current_piece(clockwise=True):
    original_shape = current_piece['shape']
    current_piece['shape'] = rotate_piece(current_piece['shape'], clockwise)
    if check_collision(current_piece['shape'], (current_piece['x'], current_piece['y'])):
        current_piece['shape'] = original_shape

# Function to handle holding piece
def hold_piece():
    global current_piece, held_piece, hold_used
    if hold_used:
        return
    if held_piece is None:
        held_piece = current_piece
        new_piece()
    else:
        held_piece, current_piece = current_piece, held_piece
    hold_used = True

# Function to draw the grid
def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = COLORS[grid[y][x]]
            pygame.draw.rect(screen, color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, (255, 255, 255), (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

# Function to draw the current piece
def draw_piece(piece, ghost=False):
    shape = piece['shape']
    off_x, off_y = piece['x'], piece['y']
    color = COLORS[piece['color']] if not ghost else (128, 128, 128)
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, ((off_x + x) * GRID_SIZE, (off_y + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Function to draw the next pieces
def draw_next_pieces():
    for i, shape in enumerate(next_pieces[:5]):
        for y, row in enumerate(SHAPES[shape]):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, COLORS[shape + 1], ((GRID_WIDTH + 1 + x) * GRID_SIZE, (i * 4 + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Function to draw the held piece
def draw_held_piece():
    if held_piece:
        shape = held_piece['shape']
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, COLORS[held_piece['color']], ((GRID_WIDTH + 1 + x) * GRID_SIZE, (16 + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

# Function to draw the ghost piece
def draw_ghost_piece():
    ghost_piece = current_piece.copy()
    while not check_collision(ghost_piece['shape'], (ghost_piece['x'], ghost_piece['y'] + 1)):
        ghost_piece['y'] += 1
    draw_piece(ghost_piece, ghost=True)

# Main game loop
screen = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
new_piece()

while not game_over:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_piece(-1, 0)
                das_timer = pygame.time.get_ticks()
            elif event.key == pygame.K_RIGHT:
                move_piece(1, 0)
                das_timer = pygame.time.get_ticks()
            elif event.key == pygame.K_DOWN:
                if not move_piece(0, 1):
                    join_piece()
            elif event.key == pygame.K_c:
                while move_piece(0, 1):
                    pass
                join_piece()
            elif event.key == pygame.K_x:
                rotate_current_piece(clockwise=False)
            elif event.key == pygame.K_UP:
                rotate_current_piece()
            elif event.key == pygame.K_z:
                rotate_current_piece()
                rotate_current_piece()
            elif event.key == pygame.K_LSHIFT:
                hold_piece()
            elif event.key == pygame.K_v:
                grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                current_piece = None
                next_pieces = generate_bag() + generate_bag()
                held_piece = None
                hold_used = False
                score = 0
                lines_cleared = 0
                start_time = time.time()
                new_piece()

    # DAS implementation
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        if pygame.time.get_ticks() - das_timer > das_delay:
            if keys[pygame.K_LEFT]:
                move_piece(-1, 0)
            elif keys[pygame.K_RIGHT]:
                move_piece(1, 0)
            das_timer = pygame.time.get_ticks()

    if lines_cleared >= 40:
        end_time = time.time()
        elapsed_time = end_time - start_time
        font = pygame.font.Font(None, 36)
        text = font.render(f'Time: {elapsed_time:.2f}s', True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        game_over = True

    draw_grid()
    draw_piece(current_piece)
    draw_ghost_piece()
    draw_next_pieces()
    draw_held_piece()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
