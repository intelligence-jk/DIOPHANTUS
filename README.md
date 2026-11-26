# DIOPHANTUS: named after Diophantus, the father of algebra: every step checked

Formerly `step-checker`.

Check that every line of a worked algebra solution follows from the line before it.

## What it solves
A student writes a solution over several lines and one line quietly breaks the chain (a sign slip, a term dropped when moving it across). This tool reads the lines, and says which line is not equivalent to the one above. Pure Python 3.10+, standard library only, exact `Fraction` arithmetic, no floating point.

## Example
File `working.txt`:
```
2(x+3)=14
2x+6=14
2x=8
x=5
```
```bash
python -m stepcheck working.txt
```
```
Line 2: ok   2x+6=14
Line 3: ok   2x=8
Line 4: NOT equivalent to line 3   x=5
```
The slip is on the last line: 2x = 8 gives x = 4.

## The maths behind it
Every line is read as a polynomial in one letter with `Fraction` coefficients. An equation `L = R` becomes the polynomial `p = L - R`. Two equations are accepted as equivalent when `q = k p` for a single non-zero constant `k`. That covers expanding brackets, moving terms across, and multiplying or dividing both sides by a number, and it is checked by comparing coefficients exactly: for `x/2 + 1 = 3` we get `p = x/2 - 2`, and for `x + 2 = 6` we get `q = x - 4 = 2p`. Multiplying only one side, such as `x + 1 = 6` from `x/2 + 1 = 3`, gives `x - 5`, which is not a multiple, so it is flagged. Two expressions (no `=`) are equivalent when their expanded polynomials are equal, for example `(x+2)(x-2)` and `x^2-4`.

Limits, on purpose: one letter per file, division only by numbers, whole-number exponents. Steps that can add or lose solutions (squaring both sides, dividing by an expression with x) are not accepted as equivalent, so they show up for you to look at.

## Install and run
```bash
python -m pip install -e .
python -m stepcheck working.txt
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
