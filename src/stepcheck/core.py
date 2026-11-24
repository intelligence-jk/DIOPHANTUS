"""Check that each line of a worked solution is equivalent to the line before.

Expressions are polynomials in one letter (default x) with exact Fraction
coefficients. Two equations are treated as equivalent when (left - right) of
one is a non-zero constant multiple of (left - right) of the other. This is
exact, and it is deliberately conservative: moves such as squaring both sides
are not accepted.
"""
from __future__ import annotations

import re
from fractions import Fraction

Poly = dict  # degree -> Fraction, zero terms removed


def _clean(p: Poly) -> Poly:
    return {d: c for d, c in p.items() if c != 0}


def _add(a: Poly, b: Poly, sign: int = 1) -> Poly:
    r = dict(a)
    for d, c in b.items():
        r[d] = r.get(d, Fraction(0)) + sign * c
    return _clean(r)


def _mul(a: Poly, b: Poly) -> Poly:
    r: Poly = {}
    for d1, c1 in a.items():
        for d2, c2 in b.items():
            r[d1 + d2] = r.get(d1 + d2, Fraction(0)) + c1 * c2
    return _clean(r)


_TOKEN = re.compile(r"\s*(\d+(?:\.\d+)?|[A-Za-z]|[-+*/()^])")


class _Parser:
    def __init__(self, text: str, var: str):
        self.var = var
        self.toks: list[str] = []
        pos = 0
        text = text.strip()
        while pos < len(text):
            m = _TOKEN.match(text, pos)
            if not m:
                raise ValueError(f"cannot read {text[pos:]!r}")
            self.toks.append(m.group(1))
            pos = m.end()
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self):
        t = self.peek()
        self.i += 1
        return t

    def parse(self) -> Poly:
        p = self.expr()
        if self.peek() is not None:
            raise ValueError(f"unexpected {self.peek()!r}")
        return p

    def expr(self) -> Poly:
        p = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            q = self.term()
            p = _add(p, q, 1 if op == "+" else -1)
        return p

    def term(self) -> Poly:
        p = self.unary()
        while True:
            t = self.peek()
            if t == "*":
                self.take()
                p = _mul(p, self.unary())
            elif t == "/":
                self.take()
                q = self.unary()
                if set(q) - {0} or not q:
                    raise ValueError("division only by a number")
                p = _mul(p, {0: 1 / q[0]})
            elif t is not None and (t == "(" or t[0].isalnum()):
                p = _mul(p, self.unary())  # implicit multiplication: 2x, 3(x+1)
            else:
                return p

    def unary(self) -> Poly:
        if self.peek() == "-":
            self.take()
            return _mul({0: Fraction(-1)}, self.unary())
        if self.peek() == "+":
            self.take()
            return self.unary()
        return self.power()

    def power(self) -> Poly:
        base = self.atom()
        if self.peek() == "^":
            self.take()
            e = self.take()
            if e is None or not e.isdigit():
                raise ValueError("exponent must be a whole number")
            r: Poly = {0: Fraction(1)}
            for _ in range(int(e)):
                r = _mul(r, base)
            return r
        return base

    def atom(self) -> Poly:
        t = self.take()
        if t is None:
            raise ValueError("expression ended early")
        if t == "(":
            p = self.expr()
            if self.take() != ")":
                raise ValueError("missing )")
            return p
        if t[0].isdigit():
            return _clean({0: Fraction(t)})
        if t.isalpha():
            if t != self.var:
                raise ValueError(f"only the letter {self.var!r} is allowed, got {t!r}")
            return {1: Fraction(1)}
        raise ValueError(f"unexpected {t!r}")


def parse_poly(text: str, var: str = "x") -> Poly:
    return _Parser(text, var).parse()


def parse_equation(text: str, var: str = "x") -> Poly:
    """Return left - right as a polynomial."""
    if text.count("=") != 1:
        raise ValueError("an equation needs exactly one '='")
    left, right = text.split("=")
    return _add(parse_poly(left, var), parse_poly(right, var), -1)


def _proportional(p: Poly, q: Poly) -> bool:
    if not p and not q:
        return True
    if not p or not q or set(p) != set(q):
        return False
    d = max(p)
    k = q[d] / p[d]
    return all(q[e] == k * p[e] for e in p)


def equivalent(a: str, b: str, var: str = "x") -> bool:
    """True if two equations (or two expressions) are the same up to a non-zero multiple."""
    if "=" in a and "=" in b:
        return _proportional(parse_equation(a, var), parse_equation(b, var))
    if "=" in a or "=" in b:
        raise ValueError("compare an equation with an equation, or an expression with an expression")
    return parse_poly(a, var) == parse_poly(b, var)


def check_steps(lines: list[str], var: str = "x") -> list[tuple[int, bool]]:
    """Result for each line after the first: (line number starting at 2, ok)."""
    out = []
    for i in range(1, len(lines)):
        out.append((i + 1, equivalent(lines[i - 1], lines[i], var)))
    return out
