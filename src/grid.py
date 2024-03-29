"""
a grid class

lets say 1 is 2x2

this is valid cause the topleft of the 2x2 block is in 3-2 position
[[0, 0, 0, 0]
 [0, 0, 0, 0]
 [0, 0, 0, 0]
 [0, 0, 1, 0]
 [0, 0, 0, 0]]

but this is not valid as it says there are four 2x2 blocks
[[0, 0, 0, 0]
 [0, 0, 0, 0]
 [0, 0, 0, 0]
 [0, 0, 1, 1]
 [0, 0, 1, 1]]
"""

from typing import List, Dict, Optional, Union

import src.config as cfg
import src.utils as utils
import src.mouse as mouse

import numpy as np

import random

import pygame


class Blocks:
    BLOCK_NONE: int = 0
    BLOCK_1x1: int = 1
    BLOCK_2x1: int = 2
    BLOCK_1x2: int = 3
    BLOCK_2x2: int = 4

    CODE: Dict[int, pygame.Surface] = {}

    @classmethod
    def load(cls) -> None:
        cls.CODE[cls.BLOCK_1x1] = utils.load_image(cfg.Paths.ASSETS / "1x1sq.png")
        cls.CODE[cls.BLOCK_2x1] = pygame.image.load(cfg.Paths.ASSETS / "2x1sq.png")
        cls.CODE[cls.BLOCK_1x2] = pygame.image.load(cfg.Paths.ASSETS / "1x2sq.png")
        cls.CODE[cls.BLOCK_2x2] = pygame.image.load(cfg.Paths.ASSETS / "2x2sq.png")


class GridVector:
    def __init__(self, row: int=0, col: int=0) -> None:
        self.row: int = row
        self.col: int = col

    @staticmethod
    def from_mouse(m: mouse.Mouse) -> 'GridVector':
        return GridVector(
            row=int((m.y - cfg.UTIL_BAR_HEIGHT) // cfg.TILE_SIZE.y),
            col=int(m.x // cfg.TILE_SIZE.x),
        )

    def __repr__(self) -> str:
        return f"grid.GridVector({self.row}, {self.col})"

    def __str__(self) -> str:
        return f"grid.GridVector({self.row}, {self.col})"

    def __eq__(self, other: "GridVector") -> bool:
        return self.row == other.row and self.col == other.col


class Grid:
    def __init__(self) -> None:
        self.rows: int = cfg.GRID_ROWS
        self.cols: int = cfg.GRID_COLS

        self.cell_size: int = cfg.TILE_SIZE.x

        self._grid: np.ndarray = np.zeros(
            (cfg.GRID_ROWS, cfg.GRID_COLS),
            dtype=np.uint8,
        )

        self.grid_surface: pygame.Surface = utils.load_image(cfg.Paths.ASSETS / "playinggrid.png")

    def set(self, grid: Union[np.ndarray, List[List[int]]]) -> None:
        assert np.array(grid).shape == self._grid.shape, f"grid shape {np.array(grid).shape} != {self._grid.shape}"
        self._grid = np.array(grid, dtype=np.uint8)

    def tobytes(self) -> bytes:
        return self._grid.tobytes()

    def get_grid(self) -> np.ndarray:
        return np.array(self._grid, dtype=np.uint8)

    def print(self) -> None:
        print(self._grid)

    def at(self, row: int, col: int) -> int:
        if not self.check_if_in_bounds(row, col):
            return 0
        return self._grid[row, col]

    def random_gen(self, counts: Dict[int, int]) -> None:
        selection = []
        for value, count in counts.items():
            selection += [value] * count

        selection_ = selection[:]

        def get_random_choice() -> int:
            if selection_:
                choice = random.choice(selection_)
                selection_.remove(choice)
                return choice
            return 0

        def is_done() -> bool:
            return not selection_

        def put_back(value__: int) -> None:
            selection_.append(value__)

        while not is_done():
            selection_ = selection[:]
            self._grid.fill(0)
            valid_places = [(row, col) for row in range(cfg.GRID_ROWS) for col in range(cfg.GRID_COLS)]
            random.shuffle(valid_places)

            for row, col in valid_places:
                choice = get_random_choice()
                if not self.set_at(row, col, choice) and choice:
                    put_back(choice)

    def set_at(self, row: int, col: int, value: int) -> bool:
        if self.if_block_at(row, col):
            return False
        if value == Blocks.BLOCK_1x1:
            self._grid[row, col] = value
            return True
        elif value == Blocks.BLOCK_2x1 and not self.if_block_at(row, col + 1):
            self._grid[row, col] = value
            return True
        elif value == Blocks.BLOCK_1x2 and not self.if_block_at(row + 1, col):
            self._grid[row, col] = value
            return True
        elif value == Blocks.BLOCK_2x2 and\
                not self.if_block_at(row, col + 1) and\
                not self.if_block_at(row + 1, col) and\
                not self.if_block_at(row + 1, col + 1):
            self._grid[row, col] = value
            return True
        return False

    def if_block_at(self, row: int, col: int) -> bool:
        return bool(self.block_at(row, col))

    def check_if_in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def block_at(self, row: int, col: int) -> int:
        if not self.check_if_in_bounds(row, col):
            return Blocks.BLOCK_2x2 * 2
        if self.at(row, col) == Blocks.BLOCK_1x1:
            return Blocks.BLOCK_1x1
        if (self.check_if_in_bounds(row, col - 1) and self.at(row, col - 1) == Blocks.BLOCK_2x1) or \
                self.at(row, col) == Blocks.BLOCK_2x1:
            return Blocks.BLOCK_2x1
        if (self.check_if_in_bounds(row - 1, col) and self.at(row - 1, col) == Blocks.BLOCK_1x2) or \
                self.at(row, col) == Blocks.BLOCK_1x2:
            return Blocks.BLOCK_1x2
        if (self.check_if_in_bounds(row - 1, col - 1) and self.at(row - 1, col - 1) == Blocks.BLOCK_2x2) or \
                self.at(row, col) == Blocks.BLOCK_2x2 or \
                (self.check_if_in_bounds(row - 1, col) and self.at(row - 1, col) == Blocks.BLOCK_2x2) or \
                (self.check_if_in_bounds(row, col - 1) and self.at(row, col - 1) == Blocks.BLOCK_2x2):
            return Blocks.BLOCK_2x2

    def locate_block(self, row: int, col: int, typ: int) -> Optional[GridVector]:
        if typ == Blocks.BLOCK_1x1 and self.at(row, col) == Blocks.BLOCK_1x1:
            return GridVector(row, col)
        elif typ == Blocks.BLOCK_2x1:
            if self.at(row, col) == Blocks.BLOCK_2x1:
                return GridVector(row, col)
            elif self.check_if_in_bounds(row, col - 1) and self.at(row, col - 1) == Blocks.BLOCK_2x1:
                return GridVector(row, col - 1)
            else:
                return None
        elif typ == Blocks.BLOCK_1x2:
            if self.at(row, col) == Blocks.BLOCK_1x2:
                return GridVector(row, col)
            elif self.check_if_in_bounds(row - 1, col) and self.at(row - 1, col) == Blocks.BLOCK_1x2:
                return GridVector(row - 1, col)
            else:
                return None
        elif typ == Blocks.BLOCK_2x2:
            if self.at(row, col) == Blocks.BLOCK_2x2:
                return GridVector(row, col)
            elif self.check_if_in_bounds(row - 1, col) and self.at(row - 1, col) == Blocks.BLOCK_2x2:
                return GridVector(row - 1, col)
            elif self.check_if_in_bounds(row, col - 1) and self.at(row, col - 1) == Blocks.BLOCK_2x2:
                return GridVector(row, col - 1)
            elif self.check_if_in_bounds(row - 1, col - 1) and self.at(row - 1, col - 1) == Blocks.BLOCK_2x2:
                return GridVector(row - 1, col - 1)
            else:
                return None
        else:
            return None

    def move_right(self, row: int, col: int) -> bool:
        cell = self.block_at(row, col)

        if cell == 0:
            return False

        if cell == Blocks.BLOCK_1x1:
            self._grid[row, col] = 0

            if self.check_if_in_bounds(row, col + 1) and not self.if_block_at(row, col + 1):
                self.set_at(row, col + 1, Blocks.BLOCK_1x1)
                self._grid[row, col] = 0
                return True

            self._grid[row, col] = Blocks.BLOCK_1x1
            return False
        elif cell == Blocks.BLOCK_2x1:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x1)
            if loc is None or loc.col == cfg.GRID_COLS - 2:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(row, col + 1) and not self.if_block_at(row, col + 2):
                self._grid[row, col + 1] = Blocks.BLOCK_2x1
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x1
            return False
        elif cell == Blocks.BLOCK_1x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_1x2)
            if loc is None or loc.col == cfg.GRID_COLS - 1:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row, loc.col + 1) and not self.if_block_at(loc.row + 1, loc.col + 1):
                self._grid[loc.row, loc.col + 1] = Blocks.BLOCK_1x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_1x2
            return False
        elif cell == Blocks.BLOCK_2x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x2)
            if loc is None or loc.col == cfg.GRID_COLS - 2:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row, loc.col + 2) and not self.if_block_at(loc.row + 1, loc.col + 2):
                self._grid[loc.row, loc.col + 1] = Blocks.BLOCK_2x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x2
            return False
        else:
            return False

    def move_left(self, row: int, col: int) -> bool:
        cell = self.block_at(row, col)

        if cell == 0:
            return False

        if cell == Blocks.BLOCK_1x1:
            self._grid[row, col] = 0

            if self.check_if_in_bounds(row, col - 1) and not self.if_block_at(row, col - 1):
                self.set_at(row, col - 1, Blocks.BLOCK_1x1)
                self._grid[row, col] = 0
                return True

            self._grid[row, col] = Blocks.BLOCK_1x1
            return False
        if cell == Blocks.BLOCK_2x1:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x1)
            if loc is None or loc.col == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(row, col - 1):
                self._grid[row, col - 1] = Blocks.BLOCK_2x1
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x1
            return False
        if cell == Blocks.BLOCK_1x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_1x2)
            if loc is None or loc.col == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row, loc.col - 1) and not self.if_block_at(loc.row + 1, loc.col - 1):
                self._grid[loc.row, loc.col - 1] = Blocks.BLOCK_1x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_1x2
            return False
        elif cell == Blocks.BLOCK_2x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x2)
            if loc is None or loc.col == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row, loc.col - 1) and not self.if_block_at(loc.row + 1, loc.col - 1):
                self._grid[loc.row, loc.col - 1] = Blocks.BLOCK_2x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x2
            return False
        else:
            return False

    def move_down(self, row: int, col: int) -> bool:
        cell = self.block_at(row, col)

        if cell == 0:
            return False

        if cell == Blocks.BLOCK_1x1:
            self._grid[row, col] = 0

            if self.check_if_in_bounds(row + 1, col) and not self.if_block_at(row + 1, col):
                self.set_at(row + 1, col, Blocks.BLOCK_1x1)
                self._grid[row, col] = 0
                return True

            self._grid[row, col] = Blocks.BLOCK_1x1
            return False
        elif cell == Blocks.BLOCK_2x1:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x1)
            if loc is None or loc.row == cfg.GRID_ROWS - 1:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row + 1, loc.col) and not self.if_block_at(loc.row + 1, loc.col + 1):
                self._grid[row + 1, col] = Blocks.BLOCK_2x1
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x1
            return False
        elif cell == Blocks.BLOCK_1x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_1x2)
            if loc is None or loc.row == cfg.GRID_ROWS - 2:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row + 2, loc.col):
                self._grid[loc.row + 1, loc.col] = Blocks.BLOCK_1x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_1x2
            return False
        elif cell == Blocks.BLOCK_2x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x2)
            if loc is None or loc.row == cfg.GRID_ROWS - 2:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row + 2, loc.col) and not self.if_block_at(loc.row + 2, loc.col + 1):
                self._grid[loc.row + 1, loc.col] = Blocks.BLOCK_2x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x2
            return False
        else:
            return False

    def move_up(self, row: int, col: int) -> bool:
        cell = self.block_at(row, col)

        if cell == 0:
            return False

        if cell == Blocks.BLOCK_1x1:
            self._grid[row, col] = 0

            if self.check_if_in_bounds(row - 1, col) and not self.if_block_at(row - 1, col):
                self.set_at(row - 1, col, Blocks.BLOCK_1x1)
                self._grid[row, col] = 0
                return True

            self._grid[row, col] = Blocks.BLOCK_1x1
            return False
        elif cell == Blocks.BLOCK_2x1:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x1)
            if loc is None or loc.row == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row - 1, loc.col) and not self.if_block_at(loc.row - 1, loc.col + 1):
                self._grid[row - 1, col] = Blocks.BLOCK_2x1
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x1
        elif cell == Blocks.BLOCK_1x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_1x2)
            if loc is None or loc.row == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row - 1, loc.col):
                self._grid[loc.row - 1, loc.col] = Blocks.BLOCK_1x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_1x2
            return False
        elif cell == Blocks.BLOCK_2x2:
            loc = self.locate_block(row, col, Blocks.BLOCK_2x2)
            if loc is None or loc.row == 0:
                return False

            self._grid[loc.row, loc.col] = 0
            if not self.if_block_at(loc.row - 1, loc.col) and not self.if_block_at(loc.row - 1, loc.col + 1):
                self._grid[loc.row - 1, loc.col] = Blocks.BLOCK_2x2
                return True

            self._grid[loc.row, loc.col] = Blocks.BLOCK_2x2
            return False
        else:
            return False

    def draw_to(self, surface: pygame.surface.Surface) -> None:
        surface.blit(self.grid_surface, (0, cfg.UTIL_BAR_HEIGHT))

        for rowi, row in enumerate(self._grid):
            for coli, value in enumerate(row):
                if value == 0:
                    continue
                x = 1 + coli + coli * self.cell_size
                y = 1 + rowi + rowi * self.cell_size + cfg.UTIL_BAR_HEIGHT
                surface.blit(Blocks.CODE[value], (x, y))

    def draw(self) -> None:
        self.draw_to(cfg.get_main_surface())
