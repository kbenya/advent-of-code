"""Advent of Code 2015 - Day 8"""

import argparse
from pathlib import Path

EXAMPLE = r"""
""
"abc"
"aaa\"aaa"
"\x27"
"""


def parse(text):
    return text.strip().splitlines()


def part1(string_literals):
    return sum(
        len(string_literal) - len(eval(string_literal))
        for string_literal in string_literals
    )


def part2(string_literals):
    return sum(
        2 + string_literal.count('"') + string_literal.count("\\")
        for string_literal in string_literals
    )


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
