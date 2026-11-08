"""Advent of Code 2015 - Day 4"""

import argparse
import hashlib
from itertools import count
from pathlib import Path

EXAMPLE = """abcdef
"""


def parse(text):
    return text.strip()


def find_lowest_number(secret_key, zero_count):
    prefix = "0" * zero_count
    for number in count(1):
        digest = hashlib.md5(f"{secret_key}{number}".encode()).hexdigest()
        if digest.startswith(prefix):
            return number


def part1(secret_key):
    return find_lowest_number(secret_key, 5)


def part2(secret_key):
    return find_lowest_number(secret_key, 6)


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
