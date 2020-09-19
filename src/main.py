from argparse import ArgumentParser
from puzzle import Puzzle


def main():
    parser = ArgumentParser(description='Solve an 8-puzzle game')
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-i', '--input',
                        action='store_true',
                        help='8-puzzle input, format of <0 1 2 3 4 5 6 7 8>')
    group.add_argument('-b', '--benchmark',
                        action='store_true',
                        help='run benchmark to calculate search cost of each depth')

    args = parser.parse_args()

    if args.benchmark:
        Puzzle.benchmark()
    else:
        if args.input:
            puzzle = Puzzle.from_stdin()
            puzzle.solve(Puzzle._manhattan_heuristic, verbosity=True)
        else:  # generate a random (guaranteed solvable)
            num_test = 3
            for _ in range(num_test):
                puzzle = Puzzle.random()
                puzzle.solve(Puzzle._manhattan_heuristic, verbosity=True)


main()
