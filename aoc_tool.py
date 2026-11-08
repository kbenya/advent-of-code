#!/usr/bin/env python3
"""Advent of Code helper.

Set up puzzles:
    python aoc_tool.py setup 2015 1              set up one day
    python aoc_tool.py setup 2015                every unlocked day of 2015
    python aoc_tool.py setup --all               every unlocked day of every year
    python aoc_tool.py setup 2015 1 --no-puzzle  skip saving puzzle.md

Refresh puzzle text and answers (e.g. part 2 after solving part 1 on the site):
    python aoc_tool.py update 2015 1             one day, always re-fetched
    python aoc_tool.py update 2015               days of 2015 not fully solved yet
    python aoc_tool.py update --all              same, for every year

Submit and check answers:
    python aoc_tool.py submit 2015 1             run solution, submit the next unsolved part
    python aoc_tool.py submit 2015 1 --part 2    choose the part yourself
    python aoc_tool.py check 2015 1              compare output with your accepted answers
    python aoc_tool.py check 2015                every day of 2015
    python aoc_tool.py check --all               every year

Each day lives in YEAR/dayDD/:
    solution.py   copied from template.py   (never overwritten)
    input.txt     your puzzle input         (downloaded once, then kept)
    puzzle.md     the puzzle text           (optional, on by default)
    answers.json  your accepted answers and known wrong guesses

solution.py must define parse(text), part1(data) and part2(data), like template.py.
Reads your session cookie from .env (AOC_SESSION=...).
Uses only the Python standard library.
"""

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "template.py"
BASE_URL = "https://adventofcode.com"
FIRST_YEAR = 2015
SECONDS_BETWEEN_REQUESTS = 1.0  # be polite to the AoC server


# ---------------------------------------------------------------- helpers


def load_env() -> None:
    """Read KEY=VALUE lines from .env into os.environ."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def days_in_year(year: int) -> int:
    """2015-2024 had 25 puzzles; from 2025 on there are 12."""
    return 25 if year <= 2024 else 12


def is_unlocked(year: int, day: int) -> bool:
    """Puzzles unlock at midnight US Eastern, which is 05:00 UTC in December."""
    unlock = dt.datetime(year, 12, day, 5, 0, tzinfo=dt.UTC)
    return dt.datetime.now(dt.UTC) >= unlock


def all_years() -> range:
    return range(FIRST_YEAR, dt.date.today().year + 1)


def day_folder(year: int, day: int) -> Path:
    return ROOT / str(year) / f"day{day:02d}"


_last_request = 0.0


def fetch(path: str, form: dict | None = None) -> str:
    """Download a page from adventofcode.com, logged in with your cookie.
    With `form`, sends a POST instead (used for submitting answers)."""
    global _last_request

    session = os.environ.get("AOC_SESSION")
    if not session:
        sys.exit(
            "No AOC_SESSION found. Copy .env.example to .env and paste your cookie in."
        )

    # Wait a little between requests so we don't hammer the site
    wait = SECONDS_BETWEEN_REQUESTS - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()

    # AoC asks automated tools to identify themselves. You can put your repo
    # URL in .env as AOC_USER_AGENT=github.com/you/advent-of-code
    user_agent = (
        os.environ.get("AOC_USER_AGENT")
        or "aoc_tool.py (personal Advent of Code helper)"
    )
    data = urllib.parse.urlencode(form).encode() if form else None
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"Cookie": f"session={session}", "User-Agent": user_agent},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.read().decode()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"Not found: {BASE_URL}{path} (puzzle not unlocked yet?)")
        if e.code in (400, 500):
            sys.exit(
                "Request failed - your session cookie is probably expired. Copy a fresh one into .env."
            )
        sys.exit(f"Request failed ({e.code}) for {BASE_URL}{path}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach adventofcode.com: {e.reason}")


# ---------------------------------------------------------------- answers


def load_answers(year: int, day: int) -> dict:
    """answers.json looks like {"1": "280", "2": "1797", "wrong": {"1": ["279"]}}"""
    path = day_folder(year, day) / "answers.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_answers(year: int, day: int, answers: dict) -> None:
    path = day_folder(year, day) / "answers.json"
    ordered = {
        k: answers[k] for k in ("1", "2", "wrong") if k in answers
    }  # readable order
    path.write_text(json.dumps(ordered, indent=2) + "\n")


def known_answer(answers: dict, part: int) -> str | None:
    return answers.get(str(part))


def fully_solved(year: int, day: int) -> bool:
    answers = load_answers(year, day)
    return bool(known_answer(answers, 1) and known_answer(answers, 2))


# ------------------------------------------------- puzzle page -> markdown


class PuzzleParser(HTMLParser):
    """Keeps only the <article class="day-desc"> blocks (part 1, and part 2
    once solved) and turns them into simple Markdown."""

    def __init__(self) -> None:
        super().__init__()
        self.in_article = False
        self.in_pre = False
        self.in_code = False
        self.href = None
        self.parts = 0
        self.out: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "day-desc" in (attrs.get("class") or ""):
            self.in_article = True
            self.parts += 1
            return
        if not self.in_article:
            return
        if tag == "h2":
            self.out.append("\n\n## ")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag == "pre":
            self.in_pre = True
            self.out.append("\n\n```\n")
        elif tag == "code" and not self.in_pre:
            self.in_code = True
            self.out.append("`")
        elif tag == "em" and not (self.in_pre or self.in_code):
            self.out.append("**")
        elif tag == "ul":
            self.out.append("\n")
        elif tag == "li":
            self.out.append("\n- ")
        elif tag == "a" and attrs.get("href"):
            self.href = attrs["href"]
            self.out.append("[")

    def handle_endtag(self, tag):
        if not self.in_article:
            return
        if tag == "article":
            self.in_article = False
        elif tag == "pre":
            self.in_pre = False
            self.out.append("```")
        elif tag == "code" and not self.in_pre:
            self.in_code = False
            self.out.append("`")
        elif tag == "em" and not (self.in_pre or self.in_code):
            self.out.append("**")
        elif tag == "ul":
            self.out.append("\n")
        elif tag == "a" and self.href:
            href = BASE_URL + self.href if self.href.startswith("/") else self.href
            self.out.append(f"]({href})")
            self.href = None

    def handle_data(self, data):
        if self.in_article:
            # Keep spacing exactly inside code blocks, tidy it everywhere else
            self.out.append(data if self.in_pre else re.sub(r"\s+", " ", data))

    def markdown(self) -> str:
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)  # trailing spaces
        text = re.sub(r"\n{3,}", "\n\n", text)  # extra blank lines
        return text.strip() + "\n"


def fetch_puzzle_page(year: int, day: int, write_md: bool = True) -> None:
    """Fetch the puzzle page once: save puzzle.md (optional) and record any
    answers the page shows as already accepted ("Your puzzle answer was ...")."""
    html = fetch(f"/{year}/day/{day}")
    folder = day_folder(year, day)

    if write_md:
        parser = PuzzleParser()
        parser.feed(html)
        if parser.parts == 0:
            print("  puzzle.md    could not find the puzzle text on the page, skipped")
        else:
            header = f"<!-- {BASE_URL}/{year}/day/{day} -->\n\n"
            (folder / "puzzle.md").write_text(header + parser.markdown())
            which = "parts 1 and 2" if parser.parts >= 2 else "part 1 only"
            print(f"  puzzle.md    saved ({which})")

    found = [
        unescape(a)
        for a in re.findall(r"Your puzzle answer was <code>(.*?)</code>", html)
    ]
    if found:
        answers = load_answers(year, day)
        for part, answer in enumerate(found, start=1):
            answers[str(part)] = answer
        save_answers(year, day, answers)
        print(f"  answers.json {len(found)} accepted answer(s) recorded")


# --------------------------------------------------------- running solutions


def load_solution(year: int, day: int):
    """Import YEAR/dayDD/solution.py as a module (its __main__ block doesn't run)."""
    path = day_folder(year, day) / "solution.py"
    if str(ROOT) not in sys.path:
        sys.path.insert(
            0, str(ROOT)
        )  # so solutions can import shared helpers from the root
    spec = importlib.util.spec_from_file_location(f"aoc_{year}_day{day:02d}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("parse", "part1", "part2"):
        if not hasattr(module, name):
            raise AttributeError(f"solution.py has no {name}() function")
    return module


def run_part(module, text: str, part: int):
    """Returns (answer as a string or None, seconds taken)."""
    start = time.perf_counter()
    data = module.parse(text)  # parse fresh each time, in case a part changes the data
    result = getattr(module, f"part{part}")(data)
    seconds = time.perf_counter() - start
    return (None if result is None else str(result).strip()), seconds


def fmt_time(seconds: float) -> str:
    return f"{seconds * 1000:.0f} ms" if seconds < 1 else f"{seconds:.2f} s"


# ---------------------------------------------------------------- commands


def setup_day(year: int, day: int, puzzle: bool = True) -> None:
    folder = day_folder(year, day)
    print(f"{year} day {day:02d}:")

    if not is_unlocked(year, day):
        print("  not unlocked yet, skipped")
        return

    folder.mkdir(parents=True, exist_ok=True)

    # 1. solution.py from the template - never overwrite your own code
    solution = folder / "solution.py"
    if solution.exists():
        print("  solution.py  already exists, left alone")
    elif not TEMPLATE.exists():
        print("  solution.py  skipped - no template.py found next to this script")
    else:
        code = TEMPLATE.read_text().replace("YEAR", str(year)).replace("DAY", str(day))
        solution.write_text(code)
        print("  solution.py  created")

    # 2. input.txt - download once, it's the same for both parts
    input_file = folder / "input.txt"
    if input_file.exists():
        print("  input.txt    already downloaded")
    else:
        input_file.write_text(fetch(f"/{year}/day/{day}/input"))
        print("  input.txt    downloaded")

    # 3. puzzle.md - only fetched if missing; use "update" to refresh it
    if puzzle:
        if (folder / "puzzle.md").exists():
            print("  puzzle.md    already saved (use 'update' to get part 2)")
        else:
            fetch_puzzle_page(year, day)


def update_day(year: int, day: int, write_md: bool = True) -> None:
    """Re-download the puzzle page: part 2 text and any answers solved on the site."""
    print(f"{year} day {day:02d}:")
    if not is_unlocked(year, day):
        print("  not unlocked yet, skipped")
        return
    day_folder(year, day).mkdir(parents=True, exist_ok=True)
    fetch_puzzle_page(year, day, write_md)


def update_many(years) -> None:
    """Re-fetch only days you've set up that aren't fully solved yet."""
    todo = [
        (year, day)
        for year in years
        for day in range(1, days_in_year(year) + 1)
        if (day_folder(year, day) / "solution.py").exists()
        and not fully_solved(year, day)
    ]
    if not todo:
        print("Nothing to update - every set-up day already has both answers.")
        return
    for year, day in todo:
        # Days set up with --no-puzzle only get their answers refreshed
        write_md = (day_folder(year, day) / "puzzle.md").exists()
        update_day(year, day, write_md)


def submit_day(year: int, day: int, part: int | None, yes: bool) -> None:
    folder = day_folder(year, day)
    if not (folder / "solution.py").exists() or not (folder / "input.txt").exists():
        sys.exit(f"Set the day up first: python aoc_tool.py setup {year} {day}")

    answers = load_answers(year, day)

    # Pick the next unsolved part if none was given
    if part is None:
        if not known_answer(answers, 1):
            part = 1
        elif not known_answer(answers, 2):
            part = 2
        else:
            print(f"{year} day {day:02d} is already fully solved. Checking instead:")
            check_day(year, day)
            return

    # Run the solution
    try:
        module = load_solution(year, day)
        answer, seconds = run_part(module, (folder / "input.txt").read_text(), part)
    except Exception:
        traceback.print_exc()
        sys.exit("\nYour solution crashed - nothing was submitted.")

    print(f"{year} day {day:02d} part {part}: {answer}   ({fmt_time(seconds)})")

    if answer is None or answer == "":
        sys.exit(f"part{part}() returned nothing - nothing to submit.")

    # Don't waste a submission on something we already know
    accepted = known_answer(answers, part)
    if accepted is not None:
        verdict = (
            "correct"
            if answer == accepted
            else f"WRONG, your accepted answer was {accepted}"
        )
        sys.exit(
            f"Part {part} is already solved - this answer is {verdict}. Not submitting."
        )
    if answer in answers.get("wrong", {}).get(str(part), []):
        sys.exit(
            f"You already submitted {answer} for part {part} and it was wrong. Not submitting."
        )

    if not yes:
        reply = input(f"Submit {answer} for part {part}? [y/N] ").strip().lower()
        if reply not in ("y", "yes"):
            print("Not submitted.")
            return

    html = fetch(f"/{year}/day/{day}/answer", form={"level": part, "answer": answer})

    # The site's reply is in the first <article> on the page
    match = re.search(r"<article>(.*?)</article>", html, re.DOTALL)
    message = unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else ""
    message = re.sub(r"\[[^\]]*\]", "", message)  # drop links like [Return to Day 1]
    message = re.sub(r"\s+", " ", message).strip()

    if "That's the right answer" in message:
        print(f"\nCorrect! ⭐  Part {part} solved.")
        answers[str(part)] = answer
        save_answers(year, day, answers)
        if part == 1:
            # Grab the part 2 text straight away
            write_md = (folder / "puzzle.md").exists()
            fetch_puzzle_page(year, day, write_md)
            if write_md:
                print("Part 2 is now in puzzle.md.")
    elif "That's not the right answer" in message:
        answers.setdefault("wrong", {}).setdefault(str(part), []).append(answer)
        save_answers(year, day, answers)
        print(f"\nWrong. {message}")
    elif "You gave an answer too recently" in message:
        print(f"\nToo soon. {message}")
    elif "You don't seem to be solving the right level" in message:
        print("\nThe site says this part is already solved (or part 1 isn't yet).")
        print("Fetching your accepted answers from the puzzle page...")
        fetch_puzzle_page(year, day, write_md=(folder / "puzzle.md").exists())
    else:
        print(f"\nUnexpected reply from the site:\n{message or html[:500]}")


def check_day(year: int, day: int, fetch_missing: bool = False) -> tuple[int, int]:
    """Run both parts and compare with accepted answers. Returns (passed, failed)."""
    folder = day_folder(year, day)
    if not (folder / "solution.py").exists() or not (folder / "input.txt").exists():
        print(f"{year} day {day:02d}: not set up")
        return 0, 0

    if fetch_missing and not fully_solved(year, day) and is_unlocked(year, day):
        print(f"{year} day {day:02d}: looking up accepted answers on the site...")
        fetch_puzzle_page(year, day, write_md=False)

    answers = load_answers(year, day)
    text = (folder / "input.txt").read_text()
    passed = failed = 0

    try:
        module = load_solution(year, day)
    except Exception as e:
        print(f"{year} day {day:02d}: could not load solution.py - {e}")
        return 0, 1

    for part in (1, 2):
        label = f"{year} day {day:02d} part {part}:"
        expected = known_answer(answers, part)
        try:
            answer, seconds = run_part(module, text, part)
        except Exception as e:
            print(f"{label} ✗ crashed - {type(e).__name__}: {e}")
            failed += 1
            continue
        took = f"({fmt_time(seconds)})"

        if answer is None:
            print(f"{label} - not written yet")
        elif expected is None:
            print(f"{label} ? {answer}  (no accepted answer known yet) {took}")
        elif answer == expected:
            print(f"{label} ✓ {answer}  {took}")
            passed += 1
        else:
            print(f"{label} ✗ got {answer}, expected {expected}  {took}")
            failed += 1
    return passed, failed


def check_many(years) -> None:
    passed = failed = 0
    for year in years:
        for day in range(1, days_in_year(year) + 1):
            if (day_folder(year, day) / "solution.py").exists():
                p, f = check_day(year, day)
                passed += p
                failed += f
    print(f"\n{passed} correct, {failed} wrong.")
    print(
        "Missing answers you solved on the website? Run: python aoc_tool.py update --all"
    )


# -------------------------------------------------------------------- main


def check_year(year: int) -> None:
    this_year = dt.date.today().year
    if not FIRST_YEAR <= year <= this_year:
        sys.exit(f"Year must be between {FIRST_YEAR} and {this_year}.")


def check_day_number(year: int, day: int) -> None:
    last = days_in_year(year)
    if not 1 <= day <= last:
        sys.exit(f"{year} has days 1 to {last}.")


def add_target_args(p, what: str) -> None:
    """year / day / --all, shared by setup, update and check."""
    p.add_argument("year", type=int, nargs="?", help="leave out with --all")
    p.add_argument(
        "day", type=int, nargs="?", help=f"leave out to {what} the whole year"
    )
    p.add_argument("--all", action="store_true", help="every year")


def resolve_target(p, args):
    """Returns ("all", None, None), ("year", year, None) or ("day", year, day)."""
    if args.all:
        if args.year is not None:
            p.error("use either --all or a year, not both")
        return "all", None, None
    if args.year is None:
        p.error("give a year (and optionally a day), or use --all")
    check_year(args.year)
    if args.day is None:
        return "year", args.year, None
    check_day_number(args.year, args.day)
    return "day", args.year, args.day


def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Advent of Code helper")
    sub = parser.add_subparsers(dest="command", required=True)

    setup = sub.add_parser(
        "setup", help="create folders, solution.py, input.txt and puzzle.md"
    )
    add_target_args(setup, "set up")
    setup.add_argument("--no-puzzle", action="store_true", help="don't save puzzle.md")

    update = sub.add_parser("update", help="re-fetch puzzle.md and accepted answers")
    add_target_args(update, "update")

    submit = sub.add_parser("submit", help="run your solution and submit the answer")
    submit.add_argument("year", type=int)
    submit.add_argument("day", type=int)
    submit.add_argument(
        "--part", type=int, choices=(1, 2), help="default: the next unsolved part"
    )
    submit.add_argument(
        "-y", "--yes", action="store_true", help="don't ask before submitting"
    )

    check = sub.add_parser(
        "check", help="compare your solutions with your accepted answers"
    )
    add_target_args(check, "check")

    args = parser.parse_args()

    if args.command == "setup":
        puzzle = not args.no_puzzle
        kind, year, day = resolve_target(setup, args)
        if kind == "all":
            for year in all_years():
                for day in range(1, days_in_year(year) + 1):
                    if is_unlocked(year, day):
                        setup_day(year, day, puzzle)
        elif kind == "year":
            for day in range(1, days_in_year(year) + 1):
                setup_day(year, day, puzzle)
        else:
            setup_day(year, day, puzzle)

    elif args.command == "update":
        kind, year, day = resolve_target(update, args)
        if kind == "all":
            update_many(all_years())
        elif kind == "year":
            update_many([year])
        else:
            update_day(year, day)  # a single day is always re-fetched

    elif args.command == "submit":
        check_year(args.year)
        check_day_number(args.year, args.day)
        submit_day(args.year, args.day, args.part, args.yes)

    elif args.command == "check":
        kind, year, day = resolve_target(check, args)
        if kind == "all":
            check_many(all_years())
        elif kind == "year":
            check_many([year])
        else:
            check_day(year, day, fetch_missing=True)


if __name__ == "__main__":
    main()
