import pygame
import random
import time

# Pygame initialization
pygame.init()

# Constants
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 30
WIDTH, HEIGHT = GRID_WIDTH * CELL_SIZE + 300, GRID_HEIGHT * CELL_SIZE
FPS = 60
DAS = 0.08  # 80ms
ARR = 0.0  # 0ms
SOFT_DROP_SPEED = 20  # Effectively instant
LOCK_DELAY = 0.5
PREVIEW_COUNT = 5

# Colors (Tetris Guideline)
COLORS = {
    0: (0, 0, 0),  # Black (empty)
    1: (0, 255, 255),  # Cyan (I)
    2: (0, 0, 255),  # Blue (J)
    3: (255, 127, 0),  # Orange (L)
    4: (255, 255, 0),  # Yellow (O)
    5: (0, 255, 0),  # Green (S)
    6: (255, 0, 0),  # Red (Z)
    7: (128, 0, 128),  # Purple (T)
    8: (192, 192, 192)  # Silver (Ghost)
}

# Shapes (Tetris Guideline)
SHAPES = {
    1: [[(0, 0), (1, 0), (2, 0), (3, 0)],  # I
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)]],
    2: [[(0, 0), (0, 1), (1, 1), (2, 1)],  # J
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)]],
    3: [[(2, 0), (0, 1), (1, 1), (2, 1)],  # L
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]],
    4: [[(0, 0), (1, 0), (0, 1), (1, 1)],  # O
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)]],
    5: [[(0, 1), (1, 1), (1, 0), (2, 0)],  # S
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 2), (1, 2), (1, 1), (2, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)]],
    6: [[(0, 0), (1, 0), (1, 1), (2, 1)],  # Z
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)]],
    7: [[(1, 0), (0, 1), (1, 1), (2, 1)],  # T
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)]]
}

SPAWN_POSITIONS = {
    1: [(3, 0), (3, 0), (3, 0), (3, 0)],  # I
    2: [(3, 1), (3, 0), (3, 0), (3, 0)],  # J
    3: [(3, 1), (3, 0), (3, 0), (3, 0)],  # L
    4: [(4, 0), (4, 0), (4, 0), (4, 0)],  # O
    5: [(3, 1), (3, 0), (3, 0), (3, 0)],  # S
    6: [(3, 1), (3, 0), (3, 0), (3, 0)],  # Z
    7: [(3, 1), (3, 0), (3, 0), (3, 0)]  # T
}

KICK_DATA = {
    1: {  # I-Piece
        0: [(-2, 0), (1, 0), (-2, -1), (1, 2)],
        1: [(-1, 0), (2, 0), (-1, 2), (2, -1)],
        2: [(2, 0), (-1, 0), (2, 1), (-1, -2)],
        3: [(1, 0), (-2, 0), (1, -2), (-2, 1)]
    },
    2: {  # Non-I Piece
        0: [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        1: [(1, 0), (1, -1), (0, 2), (1, 2)],
        2: [(1, 0), (1, 1), (0, -2), (1, -2)],
        3: [(-1, 0), (-1, -1), (0, 2), (-1, 2)]
    },
    3: {  # 180 Rotation
        0: [(0, 0)],
        1: [(0, 0)],
        2: [(0, 0)],
        3: [(0, 0)]
    }
}

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris Sprint")
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)


# Game functions
def create_bag():
    bag = [1, 2, 3, 4, 5, 6, 7]
    random.shuffle(bag)
    return bag


def get_new_piece(bag):
    if not bag:
        bag = create_bag()
    next_piece = bag.pop(0)
    return next_piece, bag


def init_piece(piece_type):
    return {
        'type': piece_type,
        'rotation': 0,
        'x': SPAWN_POSITIONS[piece_type][0][0],
        'y': SPAWN_POSITIONS[piece_type][0][1],
        'lock_delay': LOCK_DELAY
    }


def rotate(piece):
    new_rotation = (piece['rotation'] + 1) % 4
    return {**piece, 'rotation': new_rotation}


def rotate_180(piece):
    new_rotation = (piece['rotation'] + 2) % 4
    return {**piece, 'rotation': new_rotation}


def check_collision(grid, piece):
    for x, y in SHAPES[piece['type']][piece['rotation']]:
        grid_x, grid_y = int(piece['x'] + x), int(piece['y'] + y)
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT or (grid_y >= 0 and grid[grid_y][grid_x] != 0):
            return True
    return False


def kick(grid, piece, new_piece):
    rotation_index = new_piece['rotation']
    kick_set = KICK_DATA[1 if piece['type'] == 1 else 2][piece['rotation']]
    for x_offset, y_offset in kick_set:
        kicked_x = new_piece['x'] + x_offset
        kicked_y = new_piece['y'] + y_offset
        kicked_piece = {**new_piece, 'x': kicked_x, 'y': kicked_y}
        if not check_collision(grid, kicked_piece):
            return kicked_piece
    return None


def kick_180(grid, piece, new_piece):
    rotation_index = new_piece['rotation']
    kick_set = KICK_DATA[3][piece['rotation']]
    for x_offset, y_offset in kick_set:
        kicked_x = new_piece['x'] + x_offset
        kicked_y = new_piece['y'] + y_offset
        kicked_piece = {**new_piece, 'x': kicked_x, 'y': kicked_y}
        if not check_collision(grid, kicked_piece):
            return kicked_piece
    return None


def hard_drop(grid, piece):
    drop = 0
    while True:
        piece['y'] += 1
        if check_collision(grid, piece):
            piece['y'] -= 1
            break
        drop += 1
    return piece, drop


def place_piece(grid, piece):
    for x, y in SHAPES[piece['type']][piece['rotation']]:
        grid_x, grid_y = piece['x'] + x, piece['y'] + y
        grid[int(grid_y)][int(grid_x)] = piece['type']


def clear_lines(grid):
    lines_cleared = 0
    new_grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    row_index = GRID_HEIGHT - 1
    for row in reversed(grid):
        if all(cell != 0 for cell in row):
            lines_cleared += 1
        else:
            new_grid[row_index] = row
            row_index -= 1
    return new_grid, lines_cleared


def draw_grid(screen, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(screen, COLORS[grid[y][x]], (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (50, 50, 50), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def draw_piece(screen, piece, offset_x=0, offset_y=0, ghost=False):
    color = COLORS[piece['type']] if not ghost else COLORS[8]
    for x, y in SHAPES[piece['type']][piece['rotation']]:
        draw_x, draw_y = (piece['x'] + x + offset_x) * CELL_SIZE, (piece['y'] + y + offset_y) * CELL_SIZE
        pygame.draw.rect(screen, color, (draw_x, draw_y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (50, 50, 50), (draw_x, draw_y, CELL_SIZE, CELL_SIZE), 1)


def draw_hold(screen, held_piece):
    text_surface = font.render("Hold:", True, (255, 255, 255))
    screen.blit(text_surface, (GRID_WIDTH * CELL_SIZE + 20, 20))
    if held_piece:
        draw_piece(screen, {'type': held_piece, 'rotation': 0, 'x': 0, 'y': 0}, offset_x=GRID_WIDTH + 1, offset_y=1)


def draw_next_pieces(screen, next_pieces):
    text_surface = font.render("Next:", True, (255, 255, 255))
    screen.blit(text_surface, (GRID_WIDTH * CELL_SIZE + 20, 150))
    for i, piece_type in enumerate(next_pieces):
        draw_piece(screen, {'type': piece_type, 'rotation': 0, 'x': 0, 'y': 0}, offset_x=GRID_WIDTH + 1,
                   offset_y=5 + i * 4)


def draw_ghost_piece(screen, grid, piece):
    ghost_piece = {**piece}
    ghost_piece, _ = hard_drop(grid, ghost_piece)
    draw_piece(screen, ghost_piece, ghost=True)


# Game loop
def game():
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    bag = create_bag()
    next_pieces = []

    # Initialize the queue with the first 6 pieces
    for _ in range(PREVIEW_COUNT + 1):
        piece, bag = get_new_piece(bag)
        next_pieces.append(piece)

    current_piece = init_piece(next_pieces.pop(0))

    held_piece = None
    can_hold = True
    game_over = False
    lines_cleared = 0
    start_time = time.time()
    das_timer = 0
    arr_timer = 0
    last_move_direction = 0  # -1 for left, 1 for right
    lock_delay_timer = 0
    hard_dropping = False
    rotating_right = False
    rotating_left = False
    rotating_180 = False
    key_repeat_delay = {}  # Dictionary to store key repeat delays

    def reset():
        nonlocal grid, bag, next_pieces, current_piece, held_piece, can_hold, game_over, lines_cleared, start_time, das_timer, arr_timer, last_move_direction, lock_delay_timer, hard_dropping, rotating_right, rotating_left, rotating_180, key_repeat_delay
        grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        bag = create_bag()
        next_pieces = []

        # Initialize the queue with the first 6 pieces
        for _ in range(PREVIEW_COUNT + 1):
            piece, bag = get_new_piece(bag)
            next_pieces.append(piece)

        current_piece = init_piece(next_pieces.pop(0))
        held_piece = None
        can_hold = True
        game_over = False
        lines_cleared = 0
        start_time = time.time()
        das_timer = 0
        arr_timer = 0
        last_move_direction = 0
        lock_delay_timer = 0
        hard_dropping = False
        rotating_right = False
        rotating_left = False
        rotating_180 = False
        key_repeat_delay = {}

    # Main game loop
    running = True
    while running:
        screen.fill((0, 0, 0))
        delta_time = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    reset()
                # Initialize key repeat delay on key down
                key_repeat_delay[event.key] = 0 if event.key not in [pygame.K_LEFT, pygame.K_RIGHT] else DAS

        keys = pygame.key.get_pressed()

        # Horizontal movement with DAS/ARR
        move_direction = 0
        if keys[pygame.K_LEFT]:
            move_direction = -1
        if keys[pygame.K_RIGHT]:
            move_direction = 1

        if move_direction != 0:
            # Move instantly to the edge
            new_x = current_piece['x']
            while True:
                new_x += move_direction
                new_piece = {**current_piece, 'x': new_x}
                if check_collision(grid, new_piece):
                    new_x -= move_direction
                    break
                current_piece = {**current_piece, 'x': new_x}
            lock_delay_timer = 0
            last_move_direction = move_direction
        else:
            last_move_direction = 0

        # Soft drop
        if keys[pygame.K_DOWN]:
            new_y = current_piece['y'] + 1
            new_piece = {**current_piece, 'y': new_y}
            if not check_collision(grid, new_piece):
                current_piece = new_piece
                lock_delay_timer = 0  # Reset lock delay on successful move
                # Add score here if you want to reward soft drops
            else:
                pass  # Do nothing if soft drop fails

        # Hard drop
        if keys[pygame.K_c] and not hard_dropping:
            hard_dropping = True
            current_piece, drop = hard_drop(grid, current_piece)
            place_piece(grid, current_piece)
            grid, lines = clear_lines(grid)
            lines_cleared += lines

            # Get new piece and add to next_pieces queue
            piece, bag = get_new_piece(bag)
            next_pieces.append(piece)
            current_piece = init_piece(next_pieces.pop(0))

            can_hold = True
            lock_delay_timer = 0
            if check_collision(grid, current_piece):
                game_over = True

        if not keys[pygame.K_c]:
            hard_dropping = False

        # Rotate right
        if keys[pygame.K_UP] and not rotating_right:
            rotating_right = True
            new_rotation = (current_piece['rotation'] + 1) % 4
            new_piece = {**current_piece, 'rotation': new_rotation}
            kicked_piece = kick(grid, current_piece, new_piece)
            if kicked_piece:
                current_piece = kicked_piece
                lock_delay_timer = 0  # Reset lock delay on successful move

        if not keys[pygame.K_UP]:
            rotating_right = False

        # Rotate left
        if keys[pygame.K_x] and not rotating_left:
            rotating_left = True
            new_rotation = (current_piece['rotation'] - 1) % 4
            new_piece = {**current_piece, 'rotation': new_rotation}
            kicked_piece = kick(grid, current_piece, new_piece)
            if kicked_piece:
                current_piece = kicked_piece
                lock_delay_timer = 0  # Reset lock delay on successful move

        if not keys[pygame.K_x]:
            rotating_left = False

        # Rotate 180
        if keys[pygame.K_z] and not rotating_180:
            rotating_180 = True
            new_rotation = (current_piece['rotation'] + 2) % 4
            new_piece = {**current_piece, 'rotation': new_rotation}
            kicked_piece = kick_180(grid, current_piece, new_piece)
            if kicked_piece:
                current_piece = kicked_piece
                lock_delay_timer = 0  # Reset lock delay on successful move

        if not keys[pygame.K_z]:
            rotating_180 = False

        # Hold piece
        if keys[pygame.K_LSHIFT] and can_hold:
            can_hold = False
            if held_piece is None:
                held_piece = current_piece['type']
                piece, bag = get_new_piece(bag)
                next_pieces.append(piece)
                current_piece = init_piece(next_pieces.pop(0))
            else:
                held_piece, current_piece['type'] = current_piece['type'], held_piece
                current_piece = init_piece(current_piece['type'])
            lock_delay_timer = 0

        # Gravity
        if not game_over:
            new_y = current_piece['y'] + delta_time * SOFT_DROP_SPEED  # Use delta_time for smooth movement
            new_piece = {**current_piece, 'y': new_y}
            if not check_collision(grid, new_piece):
                current_piece = new_piece
                lock_delay_timer = 0
            else:
                lock_delay_timer += delta_time
                if lock_delay_timer >= LOCK_DELAY:
                    place_piece(grid, current_piece)
                    grid, lines = clear_lines(grid)
                    lines_cleared += lines

                    # Get new piece and add to next_pieces queue
                    piece, bag = get_new_piece(bag)
                    next_pieces.append(piece)
                    current_piece = init_piece(next_pieces.pop(0))

                    can_hold = True
                    lock_delay_timer = 0
                    if check_collision(grid, current_piece):
                        game_over = True

        # Drawing
        draw_grid(screen, grid)

        # Fix ghost piece jitter by using integer y position for ghost piece calculation
        ghost_piece = {**current_piece, 'y': int(current_piece['y'])}
        draw_ghost_piece(screen, grid, ghost_piece)

        draw_piece(screen, current_piece)
        draw_hold(screen, held_piece)
        draw_next_pieces(screen, next_pieces)

        # Display lines cleared
        lines_text = font.render(f"Lines: {lines_cleared}", True, (255, 255, 255))
        screen.blit(lines_text, (GRID_WIDTH * CELL_SIZE + 20, 250))

        # Game over condition
        if game_over:
            end_time = time.time()
            final_time = end_time - start_time
            game_over_text = font.render(f"Game Over! Time: {final_time:.2f}s", True, (255, 255, 255))
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 18))

        # Win condition
        if lines_cleared >= 40:
            end_time = time.time()
            final_time = end_time - start_time
            win_text = font.render(f"40 Lines! Time: {final_time:.2f}s", True, (255, 255, 255))
            screen.blit(win_text, (WIDTH // 2 - 150, HEIGHT // 2 - 18))
            game_over = True

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    game()
