from typing import Iterable, IO
from itertools import product as iter_prod
from random import Random
import numpy as np


class Minesweeper:

    def __init__(self, rows: int, columns: int, mines: int, seed=None, first_safe=False):
        self.grid: set[tuple[int, int]] = None
        self.stepped: set[tuple[int, int]] = None
        self._mines: set[tuple[int, int]] = None
        self.flagged: set[tuple[int, int]] = None
        self._ignore_mine: bool = None
        self.col_count = columns
        self.row_count = rows
        self.mine_count = mines
        self.first_safe = first_safe
        self.random = Random(seed)
        self.reset()

    def reset(self):
        self.grid = {(row, col) for row, col in iter_prod(range(self.row_count), range(self.col_count))}
        self.stepped = set()
        self._mines = set(self.random.sample(tuple(self.grid), self.mine_count))
        self.flagged = set()
        self._ignore_mine = self.first_safe

    def winning_state(self):
        if len(self.stepped & self._mines) > 0:
            return False
        if self.mines_remaining() == 0:
            return True
        return False

    def neighbours(self, cell: tuple[int, int]) -> set[tuple[int, int]]:
        naive_neighbours = set((cell[0] + row, cell[1] + col) for row, col in iter_square(range(-1, 2)))
        naive_neighbours.remove(cell)
        return set.intersection(self.grid, naive_neighbours)

    def cell_value(self, cell: tuple[int, int]) -> int:
        if cell not in self.stepped:
            raise ValueError("That's cheating!")
        return len(set.intersection(self.neighbours(cell), self._mines))

    def step(self, cell: tuple[int, int], f: IO = None) -> int:
        self.stepped.add(cell)
        if cell in self._mines:
            if self._ignore_mine:
                new_mine = self.random.choice(tuple(self.grid - self.stepped - self._mines))
                self._mines.remove(cell)
                self._mines.add(new_mine)
                if f:
                    f.write(f"""    values = np.array({str(self.get_board()).replace(" ", ",")})
    self.remove(cell_nums)
    cell_nums=Group(*(Text(str(v),color=colors[v],font_size=32/0.75*tile_size) if v<9 else mine_cell.copy() for v in values.flatten()))
    for index in range(rows * cols): cell_nums[index].move_to(cell_grid[index])
    self.bring_to_back(cell_nums)
""")
            else:
                raise ValueError("Boom!")
        self._ignore_mine = False
        return self.cell_value(cell)

    def flag(self, cell: tuple[int, int]) -> bool:
        if cell in self.stepped:
            return False
        self.flagged.add(cell)
        return True

    def mines_remaining(self):
        return len(self._mines - self.flagged)

    def tiles_remaining(self):
        return len(self.grid - self.stepped - self.flagged)

    def draw(self, **kwargs):
        show_mines = kwargs['show_mines'] if "show_mines" in kwargs.keys() else False
        coloured = kwargs['coloured'] if 'coloured' in kwargs.keys() else False
        highlighted = kwargs['highlighted'] if "highlighted" in kwargs.keys() else (-1, -1)
        underlined = kwargs['underlined'] if 'underlined' in kwargs.keys() else (-1, -1)
        bold = kwargs['bold'] if 'bold' in kwargs.keys() else (-1, -1)
        italic = kwargs['italic'] if 'italic' in kwargs.keys() else (-1, -1)
        end = kwargs['end'] if 'end' in kwargs.keys() else "\n"
        if highlighted.__class__ is not list:
            highlighted = [highlighted]
        if underlined.__class__ is not list:
            underlined = [underlined]
        if bold.__class__ is not list:
            bold = [bold]
        if italic.__class__ is not list:
            italic = [italic]
        for row in range(self.row_count):
            for col in range(self.col_count):
                if (row, col) in highlighted:
                    print("\x1b[103m", end="")
                if (row, col) in underlined:
                    print("\x1b[4m", end="")
                if (row, col) in bold:
                    print("\x1b[1m", end="")
                if (row, col) in italic:
                    print("\x1b[3m", end="")
                if (row, col) in self.stepped:
                    if (row, col) in self._mines:
                        print("\x1b[91mX" if coloured else "X", end="\x1b[m " if coloured else " ")
                    else:
                        value = self.cell_value((row, col))
                        if coloured:
                            print(f"\x1b[3{value}m{value}", end="\x1b[m ")
                        else:
                            print(value, end=" ")
                elif (row, col) in self.flagged:
                    print("\x1b[94mF" if coloured else "F", end="\x1b[m " if coloured else " ")
                else:
                    if show_mines and (row, col) in self._mines:
                        print("\x1b[91mM" if coloured else "M", end="\x1b[m " if coloured else " ")
                    else:
                        print("#", end=" ")
            print()
        print(end=end)

    def get_board(self) -> np.ndarray:
        board = np.zeros((self.row_count, self.col_count), dtype=np.int8)
        for cell in iter_prod(range(self.row_count), range(self.col_count)):
            board[cell] = len(set.intersection(self.neighbours(cell), self._mines))
        for mine in self._mines:
            board[mine] = 9
        return board


def iter_square(i: Iterable) -> Iterable:
    return iter_prod(i, i)


def ansi_seq(*args):
    return "\x1b[" + ";".join(args) + "m"
