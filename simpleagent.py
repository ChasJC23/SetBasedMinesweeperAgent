from game import Minesweeper
from random import Random


class SimpleAgent:

    def __init__(self, game: Minesweeper, seed=None):
        self.game = game
        self.random = Random(seed)

    def primitive(self, c: tuple[int, int]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        to_step = set()
        to_flag = set()
        not_stepped_neighbours = self.game.neighbours(c) - self.game.stepped
        if len(not_stepped_neighbours) == self.game.cell_value(c):
            to_flag = not_stepped_neighbours - self.game.flagged
        if len(not_stepped_neighbours & self.game.flagged) == self.game.cell_value(c):
            to_step = not_stepped_neighbours - self.game.flagged
        return to_step, to_flag

    def play(self, **kwargs):
        show_mines = kwargs['show_mines'] if "show_mines" in kwargs.keys() else False
        coloured = kwargs['coloured'] if 'coloured' in kwargs.keys() else False
        verbosity = kwargs['verbosity'] if 'verbosity' in kwargs.keys() else 0
        # the tiles we know we need to step onto next
        to_step = {(self.random.randrange(self.game.row_count), self.random.randrange(self.game.col_count))}
        # the tiles we know to flag next
        to_flag = set()
        # the tiles we have already stepped onto but have yet to use the information of
        to_search = set()
        while self.game.flagged | self.game.stepped != self.game.grid:
            # flag a tile we know we should flag
            if len(to_flag) > 0:
                tile = to_flag.pop()
                self.game.flag(tile)
                for neighbour in self.game.neighbours(tile) & self.game.stepped:
                    to_search.add(neighbour)
            # step onto a tile we know we should step onto
            if len(to_step) > 0:
                tile = to_step.pop()
                try:
                    self.game.step(tile)
                except ValueError:
                    break
                to_search.add(tile)
                for neighbour in self.game.neighbours(tile) & self.game.stepped:
                    to_search.add(neighbour)
            # search a tile we know we should search
            if len(to_search) > 0:
                tile = to_search.pop()
                new_steps, new_flags = self.primitive(tile)
                to_step |= new_steps
                to_flag |= new_flags
            if len(to_step) + len(to_flag) + len(to_search) == 0:
                try:
                    tile = self.random.choice(list(self.game.grid - self.game.flagged - self.game.stepped))
                    to_step.add(tile)
                except IndexError:
                    break
            if verbosity > 2:
                self.game.draw(show_mines=show_mines, coloured=coloured)
        if verbosity > 1:
            self.game.draw(show_mines=show_mines, coloured=coloured)
