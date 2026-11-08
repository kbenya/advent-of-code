"""Advent of Code 2015 - Day 1"""

import argparse
from pathlib import Path

EXAMPLE = """\
paste the example from the puzzle here
"""


def parse(text):
    return text.strip()


def part1(instructions):
    return instructions.count("(") - instructions.count(")")


def part2(instructions):
    floor = 0
    for position, char in enumerate(instructions, start=1):
        floor += 1 if char == "(" else -1
        if floor < 0:
            return position

    raise ValueError("Santa never enters the basement")


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
