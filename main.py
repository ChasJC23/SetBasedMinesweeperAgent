from simpleagent import SimpleAgent
from setagent import SetAgent
from game import Minesweeper
import argparse
from random import Random


# Windows difficulties:
# - Beginner:      9,  9, 10
# - Intermediate: 16, 16, 40
# - Expert:       16, 30, 99


def init():
    global args
    parser = argparse.ArgumentParser(description="Play an automated game of minesweeper")
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument("-s", "--seed",
                            help="Specify the seed for the game",
                            type=int,
                            default=None)
    seed_pair_group = seed_group.add_argument_group()
    seed_pair_group.add_argument("--board-seed",
                                 help="Specify the seed for the game board",
                                 type=int)
    seed_pair_group.add_argument("--agent-seed",
                                 help="Specify the seed for the game agent",
                                 type=int)
    parser.add_argument("-a", "--agent",
                        help="Specify the agent to play the game",
                        choices=["simple", "set"],
                        default="set")
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument("-d", "--difficulty",
                            help="Specify the difficulty of the board using defaults from the original game",
                            choices=["beginner", "intermediate", "expert"],
                            default="expert")
    dimensions_group = size_group.add_argument_group()
    dimensions_group.add_argument("-r", "--rows", "-H", "--height",
                                  help="Specify the number of rows of the board",
                                  type=int,
                                  default=16)
    dimensions_group.add_argument("-c", "--columns", "-W", "--width",
                                  help="Specify the number of columns of the board",
                                  type=int,
                                  default=30)
    dimensions_group.add_argument("-m", "--mines",
                                  help="Specify the mine count of the board",
                                  type=int,
                                  default=99)
    parser.add_argument("-C", "--coloured",
                        help="Specify whether the board is coloured in previews",
                        action="store_true")
    parser.add_argument("-v", "--verbosity",
                        help="Increase output verbosity",
                        action="count")
    parser.add_argument("--show-mines",
                        help="Show the location of all mines on the board",
                        action="store_true")
    parser.add_argument("--show-strategy",
                        help="Highlight cells indicating the strategy of the currently playing AI. "
                             "Has no effect if verbosity is less than 3",
                        action="store_true")
    parser.add_argument("--play-count",
                        help="The number of times the bot should play",
                        type=int,
                        default=1)
    parser.add_argument("--step-by-step",
                        help="Enables pausing the program at notable moments",
                        action="store_true")
    parser.add_argument("--first-safe",
                        help="Ensures the first tile clicked cannot be a mine",
                        action="store_true")
    parser.add_argument("--manim-src",
                        help="File location for generated manimation source file for this game.",
                        default=None)
    parser.add_argument("--cell-graphic-path",
                        help="File location for cell graphic used in the generated manimation source file.",
                        default=None)
    parser.add_argument("--flag-graphic-path",
                        help="File location for the flagged cell graphic used in the generated manimation source file.",
                        default=None)
    parser.add_argument("--mine-graphic-path",
                        help="File location for the mine graphic used in the generated manimation source file.",
                        default=None)
    args = parser.parse_args()


def main():
    random = Random(args.seed)
    if args.board_seed is None:
        args.board_seed = random.getrandbits(64)
        print(f"Board seed: {args.board_seed}")
    if args.agent_seed is None:
        args.agent_seed = random.getrandbits(64)
        print(f"Agent seed: {args.agent_seed}")
    if args.verbosity is None:
        args.verbosity = 0
    match args.difficulty:
        case "beginner":
            args.rows = 9
            args.columns = 9
            args.mines = 10
        case "intermediate":
            args.rows = 16
            args.columns = 16
            args.mines = 40
        case "expert":
            args.rows = 16
            args.columns = 30
            args.mines = 99
        case _:
            pass
    game = Minesweeper(args.rows, args.columns, args.mines, args.board_seed, first_safe=args.first_safe)
    match args.agent:
        case "set":
            agent = SetAgent(game, seed=args.agent_seed)
        case "simple":
            agent = SimpleAgent(game, seed=args.agent_seed)
        case _:
            return
    win_count = 0
    if args.manim_src:
        manim_file = open(args.manim_src, 'w')
        manim_file.write(f"from manim import *\nimport numpy as np\nclass S{hex(args.board_seed)[2:]}{hex(args.agent_seed)[2:]}(Scene):\n  def construct(self):\n    pass\n")
    else:
        manim_file = None
    try:
        for i in range(args.play_count):
            game.reset()
            agent.play(show_mines=args.show_mines, coloured=args.coloured, verbosity=args.verbosity,
                       show_strategy=args.show_strategy, step_by_step=args.step_by_step, manim_file=manim_file)
            if args.step_by_step and args.play_count > 1:
                input()
            if game.winning_state():
                win_count += 1
            if args.verbosity < 1:
                print(
                    f"\r[{'=' * int(60 * (i + 1) / args.play_count)}{' ' * int(60 - 60 * (i + 1) / args.play_count)}] {'{:.1f}'.format((i + 1) / args.play_count * 100)}% ({'{:.1f}'.format(win_count / (i + 1) * 100)}%)",
                    end="")
    except KeyboardInterrupt:
        if args.verbosity < 1:
            print()
    print()
    print(f"Won {win_count} out of {i+1} games ({win_count / (i+1) * 100}%)")
    if manim_file:
        manim_file.close()


if __name__ == '__main__':
    args: argparse.Namespace
    init()
    main()
