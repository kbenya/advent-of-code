"""Advent of Code 2015 - Day 6"""

import argparse
from pathlib import Path

EXAMPLE = """\
turn on 0,0 through 999,999
toggle 0,0 through 999,0
turn off 499,499 through 500,500
"""


def parse(text):
    instructions = []
    for line in text.strip().splitlines():
        *action_words, start, _, end = line.split()
        x_start, y_start = map(int, start.split(","))
        x_end, y_end = map(int, end.split(","))
        instructions.append((" ".join(action_words), x_start, y_start, x_end, y_end))
    return instructions


def part1(instructions):
    grid = [[0] * 1000 for _ in range(1000)]
    for action, x_start, y_start, x_end, y_end in instructions:
        columns = slice(y_start, y_end + 1)
        width = y_end - y_start + 1
        for x in range(x_start, x_end + 1):
            row = grid[x]
            if action == "turn on":
                row[columns] = [1] * width
            elif action == "turn off":
                row[columns] = [0] * width
            else:  # toggle
                row[columns] = [1 - light for light in row[columns]]
    return sum(map(sum, grid))


def part2(instructions):
    grid = [[0] * 1000 for _ in range(1000)]
    for action, x_start, y_start, x_end, y_end in instructions:
        columns = slice(y_start, y_end + 1)
        for x in range(x_start, x_end + 1):
            row = grid[x]
            if action == "turn on":
                row[columns] = [brightness + 1 for brightness in row[columns]]
            elif action == "turn off":
                row[columns] = [max(brightness - 1, 0) for brightness in row[columns]]
            else:  # toggle
                row[columns] = [brightness + 2 for brightness in row[columns]]
    return sum(map(sum, grid))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--example", action="store_true", help="run on the example"
    )
    args = parser.parse_args()

    if args.example:
        text = EXAMPLE
    else:
        text = (Path(__file__).parent / "input.txt").read_text()

    data = parse(text)
    print("Part 1:", part1(data))
    print("Part 2:", part2(data))
