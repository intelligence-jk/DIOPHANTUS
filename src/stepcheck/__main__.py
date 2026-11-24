"""python -m stepcheck FILE   (one line of working per line; '-' reads stdin)"""
import sys

from .core import check_steps


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m stepcheck FILE", file=sys.stderr)
        return 2
    text = sys.stdin.read() if args[0] == "-" else open(args[0]).read()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        print("Need at least two lines.", file=sys.stderr)
        return 2
    bad = 0
    for n, ok in check_steps(lines):
        print(f"Line {n}: {'ok' if ok else 'NOT equivalent to line ' + str(n - 1)}   {lines[n - 1]}")
        bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
