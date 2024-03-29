from typing import List, Tuple, Union, Optional, Dict

import src.config as cfg

import src.colors as colors
import src.button as button
import src.grid as grid
import src.mouse as mouse
import src.solution as solution

import numpy as np

import random
import pygame
import time
import math
import sys
import os


class Game:
    def __init__(self, WIN: pygame.surface.Surface):
        # display related attributes
        self.SCREEN_SIZE: pygame.Vector2 = pygame.Vector2(WIN.get_size())
        self.W: int = self.SCREEN_SIZE.x
        self.H: int = self.SCREEN_SIZE.y
        self.WIN: pygame.surface.Surface = WIN

        # clock related attributes
        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.click_pos: Optional[pygame.Vector2] = None
        self.grid_pos: Optional[grid.GridVector] = None
        self.true_block_pos: Optional[grid.GridVector] = None

        # UI elements
        self.reset_button: button.Button = button.Button(cfg.WIDTH - 30 - cfg.RESET_WIDTH, cfg.UTIL_BAR_HEIGHT / 2 - cfg.RESET_HEIGHT / 2, cfg.RESET_WIDTH, cfg.RESET_HEIGHT)

        # game objects
        self.mouse: mouse.Mouse = mouse.Mouse.create()
        self.grid: grid.Grid = grid.Grid()
        self.solution: solution.Solution = solution.Solution()

        self.generate_grids()

        self.start_time: float = time.time()

    def generate_grids(self) -> None:

        counts = self.gen_random_counts()

        self.solution.random_gen(counts)
        self.grid.random_gen(counts)

    @staticmethod
    def gen_random_counts() -> Dict[int, int]:
        total_blocks = 11
        b_1x1 = random.randrange(3, 6)
        total_blocks -= b_1x1
        b_2x1 = int(random.randrange(0, int(total_blocks // 2)) // 2)
        total_blocks -= b_2x1 * 2
        b_1x2 = int(total_blocks // 2)

        return {
            grid.Blocks.BLOCK_1x1: b_1x1,
            grid.Blocks.BLOCK_2x1: b_2x1,
            grid.Blocks.BLOCK_1x2: b_1x2,
            grid.Blocks.BLOCK_2x2: 1
        }

    def reset(self) -> None:
        self.generate_grids()
        self.start_time = time.time()

    def won(self) -> None:
        font = cfg.get_font(None, 50)
        text = font.render("You Won!", True, colors.black)
        text_rect = text.get_rect()
        text_rect.center = (self.W / 2, self.H / 2)

        self.draw()
        self.WIN.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(3000)

        self.reset()

    def update(self) -> None:
        if np.array_equal(self.grid.get_grid(), self.solution.get_grid()):
            self.won()

    def event_handler(self) -> None:
        events = pygame.event.get()

        self.mouse.update(events)

        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        if self.mouse.just_pressed_left:
            if self.mouse.y > cfg.UTIL_BAR_HEIGHT:
                col = int(self.mouse.x // cfg.TILE_SIZE.x)
                row = int((self.mouse.y - cfg.UTIL_BAR_HEIGHT) // cfg.TILE_SIZE.y)

                if not self.grid.if_block_at(row, col):
                    return

                cell = self.grid.block_at(row, col)
                self.true_block_pos = self.grid.locate_block(row, col, cell)

                self.click_pos = pygame.Vector2(self.mouse.x, self.mouse.y)
                self.grid_pos = grid.GridVector.from_mouse(self.mouse)
            elif self.reset_button.is_over(self.mouse.pos):
                self.reset()

        if self.mouse.just_released_left:
            if self.click_pos is not None:
                self.click_pos = None
                self.grid_pos = None
                self.true_block_pos = None

        if self.grid_pos is not None:
            new_grid_pos = grid.GridVector.from_mouse(self.mouse)

            if self.grid_pos == new_grid_pos:
                return

            if self.grid_pos.col < new_grid_pos.col < cfg.GRID_COLS:
                if self.grid.move_right(self.true_block_pos.row, self.true_block_pos.col):
                    self.true_block_pos.col += 1
            elif -1 < new_grid_pos.col < self.grid_pos.col:
                if self.grid.move_left(self.true_block_pos.row, self.true_block_pos.col):
                    self.true_block_pos.col -= 1

            if self.grid_pos.row < new_grid_pos.row < cfg.GRID_ROWS:
                if self.grid.move_down(self.true_block_pos.row, self.true_block_pos.col):
                    self.true_block_pos.row += 1
            elif -1 < new_grid_pos.row < self.grid_pos.row:
                if self.grid.move_up(self.true_block_pos.row, self.true_block_pos.col):
                    self.true_block_pos.row -= 1

            self.grid_pos = new_grid_pos

    def draw(self) -> None:
        self.WIN.fill((30, 30, 30))

        pygame.draw.rect(self.WIN, colors.grey9, [0, 0, cfg.WIDTH, cfg.UTIL_BAR_HEIGHT])

        self.reset_button.draw_to(self.WIN, colors.red)

        time_since_start_in_s = time.time() - self.start_time

        minutes = int(time_since_start_in_s // 60)
        seconds = int(time_since_start_in_s % 60)
        time_font = cfg.get_font(None, 40)
        time_text = time_font.render(f"{minutes}:{seconds}", True, colors.black)

        time_text_rect = time_text.get_rect()
        time_text_rect.centerx = cfg.WIDTH / 2
        time_text_rect.y = 5

        pygame.draw.rect(self.WIN, colors.orange, [cfg.WIDTH / 2 - 60 / 2, 5, 60, time_text_rect.height])
        self.WIN.blit(time_text, time_text_rect)

        self.solution.draw_to(self.WIN)
        self.grid.draw_to(self.WIN)

        pygame.display.update()

    def run(self) -> None:
        while self.running:
            self.clock.tick(cfg.FPS)
            self.event_handler()
            self.update()
            self.draw()
