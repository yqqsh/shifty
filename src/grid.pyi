from typing import Dict, List, Union, Optional

import src.mouse as mouse

import numpy as np

import pygame


class Blocks:
    BLOCK_NONE: int
    BLOCK_1x1: int
    BLOCK_2x1: int
    BLOCK_1x2: int
    BLOCK_2x2: int

    CODE: Dict[int, pygame.Surface]

    @classmethod
    def load(cls) -> None: ...

class GridVector:
    row: int
    col: int

    def __init__(self, row: int=0, col: int=0) -> None: ...
    @staticmethod
    def from_mouse(m: mouse.Mouse) -> "GridVector": ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: GridVector) -> bool: ...


class Grid:
    rows: int
    cols: int
    cell_size: int
    _grid: np.ndarray
    grid_surface: pygame.Surface
    def __init__(self) -> None: ...
    def draw_to(self, surface: pygame.Surface) -> None: ...
    def draw(self) -> None: ...
    def at(self, row: int, col: int) -> int: ...
    def set_at(self, row: int, col: int, value: int) -> None: ...
    def locate_block(self, row: int, col: int, typ: int) -> Optional[GridVector]: ...
    def set(self, grid: Union[np.ndarray, List[List[int]]]) -> None: ...
    def move_right(self, row: int, col: int) -> bool: ...
    def move_left(self, row: int, col: int) -> bool: ...
    def move_down(self, row: int, col: int) -> bool: ...
    def move_up(self, row: int, col: int) -> bool: ...
    def check_if_in_bounds(self, row: int, col: int) -> bool: ...
    def if_block_at(self, row: int, col: int) -> bool: ...
    def block_at(self, row: int, col: int) -> int: ...
    def print(self) -> None: ...
