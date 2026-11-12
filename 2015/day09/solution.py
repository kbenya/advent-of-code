"""Advent of Code 2015 - Day 9"""

import argparse
from itertools import pairwise, permutations
from pathlib import Path

EXAMPLE = """
London to Dublin = 464
London to Belfast = 518
Dublin to Belfast = 141
"""


def parse(text):
    distances = {}
    towns = set()
    for line in text.strip().splitlines():
        town_a, _, town_b, _, distance = line.split()  # "London to Dublin = 464"
        distances[town_a, town_b] = distances[town_b, town_a] = int(distance)
        towns.update((town_a, town_b))
    return distances, towns


def part1(data):
    distances, towns = data
    return min(
        sum(distances[from_town, to_town] for from_town, to_town in pairwise(route))
        for route in permutations(towns)
    )


def part2(data):
    distances, towns = data
    return max(
        sum(distances[from_town, to_town] for from_town, to_town in pairwise(route))
        for route in permutations(towns)
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
