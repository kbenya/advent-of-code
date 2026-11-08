"""Advent of Code 2015 - Day 3"""

import argparse
from pathlib import Path

EXAMPLE = "^v^v^v^v^v"

STEP_BY_ARROW = {"^": 1j, "v": -1j, ">": 1, "<": -1}


def parse(text):
    return text.strip()


def positions_visited(moves):
    position = 0
    visited = {position}
    for move in moves:
        position += STEP_BY_ARROW[move]
        visited.add(position)
    return visited


def part1(moves):
    return len(positions_visited(moves))


def part2(moves):
    return len(positions_visited(moves[::2]) | positions_visited(moves[1::2]))


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
