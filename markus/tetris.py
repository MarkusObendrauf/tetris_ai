from dataclasses import dataclass
from queue import Queue
import pygame
from active_tetramino import ActiveTetramino
from grid import Grid
from queue import QUEUE_PIECE_HEIGHT, VISIBLE_QUEUE_LENGTH

pygame.font.init()
FONT = pygame.font.Font(pygame.font.get_default_font(), 32)

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
S_WIDTH = 800
S_HEIGHT = 700
BLOCK_SIZE = 32
PLAY_WIDTH = BLOCK_SIZE * Grid.WIDTH
PLAY_HEIGHT = BLOCK_SIZE * Grid.HEIGHT

top_left_x = (S_WIDTH - PLAY_WIDTH) // 2
top_left_y = S_HEIGHT - PLAY_HEIGHT

DAS = 80


@dataclass
class GameState:
    grid: Grid
    active_tetramino: ActiveTetramino
    queue: Queue

    fall_timer: int = 0
    right_held: bool = False
    right_das_timer: int = 0
    left_held: bool = False
    left_das_timer: int = 0


def draw(window: pygame.Surface, gs: GameState):
    window.fill((0, 0, 0))

    grid_surface = window.subsurface(
        (
            WINDOW_WIDTH // 2 - Grid.WIDTH * BLOCK_SIZE // 2,
            WINDOW_HEIGHT - PLAY_HEIGHT,
            BLOCK_SIZE * Grid.WIDTH,
            BLOCK_SIZE * Grid.HEIGHT,
        ),
    )
    queue_surface = window.subsurface(
        (
            WINDOW_WIDTH - 6 * BLOCK_SIZE,
            WINDOW_HEIGHT - PLAY_HEIGHT,
            BLOCK_SIZE * 4,
            BLOCK_SIZE * QUEUE_PIECE_HEIGHT * VISIBLE_QUEUE_LENGTH,
        ),
    )

    gs.grid.draw(grid_surface, BLOCK_SIZE)
    gs.active_tetramino.draw_ghost(grid_surface, BLOCK_SIZE)
    gs.active_tetramino.draw(grid_surface, BLOCK_SIZE)
    gs.queue.draw(queue_surface, BLOCK_SIZE)
    gs.grid.draw_gridlines(grid_surface, BLOCK_SIZE)
    pygame.display.update()


def main(window: pygame.Surface):
    queue = Queue()
    active_tetramino = ActiveTetramino(queue.pop())

    gs = GameState(Grid.get(), active_tetramino, queue)

    lock_piece = False
    run = True
    clock = pygame.time.Clock()

    while run:
        gs.fall_timer += clock.get_rawtime()
        if gs.left_held:
            gs.left_das_timer += clock.get_rawtime()
        if gs.right_held:
            gs.right_das_timer += clock.get_rawtime()
        clock.tick()

        if gs.fall_timer / 1000 > 1:
            gs.fall_timer = 0
            valid = gs.active_tetramino.move_down()
            if not valid:
                lock_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    gs.left_held = False
                    gs.left_das_timer = 0
                if event.key == pygame.K_RIGHT:
                    gs.right_held = False
                    gs.right_das_timer = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    gs.active_tetramino.move_left()
                    gs.left_held = True
                if event.key == pygame.K_RIGHT:
                    gs.right_held = True
                    gs.active_tetramino.move_right()
                if event.key == pygame.K_DOWN:
                    while gs.active_tetramino.move_down():
                        pass
                    gs.fall_timer = 0
                if event.key == pygame.K_UP:
                    gs.active_tetramino.rotate_cw()
                if event.key == pygame.K_x:
                    gs.active_tetramino.rotate_ccw()
                if event.key == pygame.K_z:
                    gs.active_tetramino.rotate_180()
                if event.key == pygame.K_c:
                    while gs.active_tetramino.move_down():
                        pass
                    lock_piece = True

        if gs.left_das_timer > DAS:
            while gs.active_tetramino.move_left():
                pass
        if gs.right_das_timer > DAS:
            while gs.active_tetramino.move_right():
                pass

        if lock_piece:
            gs.grid.insert_piece(gs.active_tetramino)
            gs.grid.clear_rows()
            gs.fall_timer = 0
            gs.active_tetramino = ActiveTetramino(queue.pop())
            lock_piece = False

        draw(window, gs)


window = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption("Tetris")
main(window)
