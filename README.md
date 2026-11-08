# Advent of Code

My solutions to [Advent of Code](https://adventofcode.com/) puzzles in Python.

## Requirements

Python 3.10 or newer. No packages to install; only the standard library is used.

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
   AOC_USER_AGENT=github.com/YOUR-USERNAME/advent-of-code
   ```
   `AOC_USER_AGENT` is optional. It identifies the script to the AoC server,
   as the site requests.

The cookie expires after about a month. If downloads start failing, copy a
fresh one.

## Running the tool

`aoc_tool.py` can be run several ways. They all do the same thing:

| Terminal                 | Command                           |
| ------------------------ | --------------------------------- |
| PowerShell               | `.\aoc_tool setup 2015 1`         |
| cmd                      | `aoc_tool setup 2015 1`           |
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

# Re-fetch the puzzle page: part 2 text + answers solved on the website
python aoc_tool.py update 2015 1              # one day (always re-fetched)
python aoc_tool.py update 2015                # days of 2015 not fully solved
python aoc_tool.py update --all               # same, for every year

# Run a solution
python 2015/day01/solution.py                 # on your puzzle input
python 2015/day01/solution.py -e              # on the example

# Submit an answer (asks before sending; picks the next unsolved part)
python aoc_tool.py submit 2015 1
python aoc_tool.py submit 2015 1 --part 2 -y

# Check that solutions still give your accepted answers
python aoc_tool.py check 2015 1
python aoc_tool.py check 2015
python aoc_tool.py check --all
```

`setup` never overwrites an existing `solution.py` or `input.txt`, so it's
always safe to run again. `submit` never sends the same wrong answer twice.

## Daily workflow

1. `python aoc_tool.py setup 2015 1`
2. Read `2015/day01/puzzle.md` and paste the example into `EXAMPLE` in `solution.py`.
3. Write `part1()` and test it with `python 2015/day01/solution.py -e`.
4. `python aoc_tool.py submit 2015 1`. Part 2 is added to `puzzle.md` once it's correct.
5. Write `part2()`, test, and submit again.
6. Commit: `git add 2015/day01 && git commit -m "2015 day 1"`.

## Structure

```
2015/
  day01/
    solution.py    # my code (committed)
    input.txt      # puzzle input (not committed)
    puzzle.md      # puzzle text (not committed)
    answers.json   # accepted answers + wrong guesses (not committed)
aoc_tool.py        # setup / update / submit / check
aoc_tool.bat       # shortcut for PowerShell / cmd
aoc_tool.sh        # shortcut for Git Bash / Linux / macOS
template.py        # copied into each new day as solution.py
```

Every `solution.py` defines `parse(text)`, `part1(data)` and `part2(data)`,
which `submit` and `check` call. Puzzle inputs and text are not committed, as
requested by the Advent of Code creator.

## Progress

| Year | Stars  |
| ---- | ------ |
| 2015 | 0 / 50 |
