"""Advent of Code 2015 - Day 17"""

import argparse
from pathlib import Path

EXAMPLE = """\
paste the example from the puzzle here
"""


def parse(text):
    return text.strip().splitlines()


def part1(data):
    return None


def part2(data):
    return None


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
