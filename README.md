# Advent of Code

My solutions to [Advent of Code](https://adventofcode.com/) puzzles in Python.

## Setup

1. Clone the repo.
2. Copy `.env.example` to `.env`.
3. Log in at [adventofcode.com](https://adventofcode.com/) and copy your
   `session` cookie:
   - **Firefox:** F12 → **Storage** → Cookies → `https://adventofcode.com`
   - **Chrome:** F12 → **Application** → Cookies → `https://adventofcode.com`
4. Paste the cookie value into `.env`:
   ```
   AOC_SESSION=your_cookie_here
   ```

The cookie expires after about a month. If downloads start failing, copy a
fresh one.

## Running the tool

`aoc_tool.py` can be run three ways. They all do the same thing:

| Terminal                 | Command                           |
| ------------------------ | --------------------------------- |
| PowerShell / cmd         | `aoc_tool setup 2015 1`           |
| Git Bash / Linux / macOS | `./aoc_tool.sh setup 2015 1`      |
| Anywhere                 | `python aoc_tool.py setup 2015 1` |

Run them from the repo root. The examples below use the Python form.

## Usage

```bash
# Set up puzzles: creates YEAR/dayDD/ with solution.py, input.txt and puzzle.md
python aoc_tool.py setup 2015 1               # one day
python aoc_tool.py setup 2015                 # every unlocked day of a year
python aoc_tool.py setup --all                # every year
python aoc_tool.py setup 2015 1 --no-puzzle   # without puzzle.md

# After solving part 1: re-fetch puzzle.md to get part 2
python aoc_tool.py update 2015 1              # one day
python aoc_tool.py update 2015                # days of 2015 still missing part 2
python aoc_tool.py update --all               # same, for every year

# Run a solution
python 2015/day01/solution.py                # on your puzzle input
python 2015/day01/solution.py -e             # on the example

# Submit an answer (asks before sending; picks the next unsolved part)
python aoc_tool.py submit 2015 1
python aoc_tool.py submit 2015 1 --part 2 -y

# Check solutions still give your accepted answers
python aoc_tool.py check 2015 1
python aoc_tool.py check --all

```

`setup` never overwrites an existing `solution.py` or `input.txt`, so it's
always safe to run again.

## Structure

Each puzzle lives in `YEAR/dayDD/solution.py`. Puzzle inputs are not committed,
as requested by the Advent of Code creator.

## Progress

| Year | Stars |
| ---- | ----- |
