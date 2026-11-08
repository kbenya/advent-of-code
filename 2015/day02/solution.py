"""Advent of Code 2015 - Day 2"""

import argparse
from pathlib import Path

EXAMPLE = """\
paste the example from the puzzle here
"""


def parse(text):
    return [sorted(map(int, line.split("x"))) for line in text.strip().splitlines()]


def part1(presents):
    total_paper = 0
    for small, mid, large in presents:
        surface = 2 * (small * mid + mid * large + large * small)
        slack = small * mid
        total_paper += surface + slack
    return total_paper


def part2(presents):
    total_ribbon = 0
    for small, mid, large in presents:
        wrap = 2 * (small + mid)
        bow = small * mid * large
        total_ribbon += wrap + bow
    return total_ribbon


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
