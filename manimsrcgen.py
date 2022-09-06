from game import Minesweeper
from typing import IO


def agent_prelim(file: IO, game: Minesweeper):
    file.write(f"""    values = np.array({str(game.get_board()).replace(" ", ",")})
    colors = [GREY, RED, GREEN, YELLOW, BLUE, PURPLE, LIGHT_BROWN, PINK, DARK_GREY]
    rows, cols = values.shape
    tile_size = min(7 / rows, 14 / cols)
    unclicked_cell=SVGMobject('/home/chascb/Pictures/minesweeper/cell.svg',height=tile_size,width=tile_size)
    flagged_cell=SVGMobject('/home/chascb/Pictures/minesweeper/flagged.svg',height=tile_size,width=tile_size)
    mine_cell=SVGMobject('/home/chascb/Pictures/minesweeper/pressedmine.svg',height=tile_size,width=tile_size)
    cell_grid = Group(*(Square(tile_size) for _ in range(rows * cols))).arrange_in_grid(rows, cols, 0)
    cells = Group(*[unclicked_cell.copy() for _ in range(rows * cols)]).arrange_in_grid(rows, cols, 0)
    cells_ani = AnimationGroup(*(GrowFromCenter(cell) for cell in cells))
    cell_nums=Group(*(Text(str(v),color=colors[v],font_size=32/0.75*tile_size) if v<9 else mine_cell.copy() for v in values.flatten()))
    flags=Group(*(flagged_cell.move_to(cells[index]).copy() for index in range(rows * cols)))
    for index in range(rows * cols): cell_nums[index].move_to(cell_grid[index])
    self.play(FadeIn(cell_grid), cells_ani)
    self.bring_to_back(cell_nums)
""")


def agent_term(file: IO):
    file.write("""    cell_grid.generate_target(True)
    cell_grid.target.shift(9 * UP)
    self.remove(flags)
    self.play(MoveToTarget(cell_grid), cells.animate.move_to(cell_grid.target), *(cell_nums[index].animate.move_to(cell_grid.target[index]) for index in range(rows * cols)))
    self.remove(cell_grid, cells, cell_nums)
""")
