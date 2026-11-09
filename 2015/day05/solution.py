"""Advent of Code 2015 - Day 5"""

import argparse
from itertools import pairwise
from pathlib import Path

EXAMPLE = """aaaa
"""


def parse(text):
    return text.strip().splitlines()


def part1(strings):
    nice_string_count = 0
    for string in strings:
        if any(pair in string for pair in ["ab", "cd", "pq", "xy"]):
            continue

        vowel_count = sum(string.count(vowel) for vowel in "aeiou")
        if vowel_count < 3:
            continue

        if any(first == second for first, second in pairwise(string)):
            nice_string_count += 1

    return nice_string_count


def part2(strings):
    nice_string_count = 0
    for string in strings:
        has_repeated_pair = False
        first_index = {}
        for start_index, pair in enumerate(pairwise(string)):
            if pair in first_index:
                if start_index - first_index[pair] >= 2:
                    has_repeated_pair = True
                    break
            else:
                first_index[pair] = start_index

        if has_repeated_pair and any(
            first == third for first, third in zip(string, string[2:])
        ):
            nice_string_count += 1

    return nice_string_count


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
