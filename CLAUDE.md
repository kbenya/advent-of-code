# Advent of Code - instructions for Claude

I solve Advent of Code puzzles myself to learn. Help me only in the ways below.

## No spoilers

- Never write, show or describe a solution for a part I haven't solved yet.
  A part is solved when it's in `YEAR/dayDD/answers.json`.
- If I ask for a **hint**, give the smallest nudge that gets me moving
  (a concept or a question to think about), not code.
- Never run `aoc_tool.py submit`. I submit my own answers.
- Don't read or change `.env`.

## Reviewing a solved day

When I ask for a review of a day:

1. Read `puzzle.md` and `solution.py` in that day's folder.
2. Run `python aoc_tool.py check YEAR DAY` to confirm it's correct.
3. Suggest improvements:
   - **Variable and function names**: point out unclear or misleading names
     (e.g. `x`, `tmp`, `data2`, `l`) and suggest clearer ones, with a short
     reason (e.g. `l` looks like `1`; `presents` says more than `items`).
   - **Readability**: structure, comments, simpler logic.
   - **Idiomatic Python**: built-ins and standard library that fit better.
   - **Speed**: only where it matters, with the reason it's faster.
     Explain _why_ each change is better, and name the concept
     (e.g. "set lookup is O(1)").
4. Show the changes as suggestions. Don't edit my file unless I say so.
5. If I accept changes, run `check` again to prove the answers still match.

## Style

- Python 3.10+, standard library only.
- Keep `parse`, `part1`, `part2` in every solution (aoc_tool.py uses them).
