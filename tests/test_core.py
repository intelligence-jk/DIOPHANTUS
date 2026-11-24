from fractions import Fraction as F

import pytest

from stepcheck import check_steps, equivalent, parse_poly
from stepcheck.__main__ import main


def test_parse_expand():
    assert parse_poly("(x+1)^2") == {2: F(1), 1: F(2), 0: F(1)}
    assert parse_poly("3(x-2)") == {1: F(3), 0: F(-6)}
    assert parse_poly("x/4 + 1/2") == {1: F(1, 4), 0: F(1, 2)}
    assert parse_poly("-(x-3)") == {1: F(-1), 0: F(3)}


def test_good_solution():
    lines = ["2(x+3)=14", "2x+6=14", "2x=8", "x=4"]
    assert check_steps(lines) == [(2, True), (3, True), (4, True)]


def test_sign_slip_found():
    lines = ["3x-5=10", "3x=5", "x=5/3"]
    res = check_steps(lines)
    assert res[0] == (2, False)


def test_multiple_of_equation_ok():
    assert equivalent("x/2+1=3", "x+2=6")
    assert equivalent("2x=8", "x=4")


def test_not_equivalent_when_scaled_one_side_only():
    assert not equivalent("x/2+1=3", "x+1=6")


def test_quadratic_rearrangement():
    assert equivalent("x^2=5x-6", "x^2-5x+6=0")
    assert not equivalent("x^2=5x-6", "x^2-5x-6=0")


def test_expressions():
    assert equivalent("(x+2)(x-2)", "x^2-4")
    assert not equivalent("(x+2)^2", "x^2+4")


def test_identity_and_contradiction_lines():
    assert equivalent("x+1=x+1", "0=0")
    assert not equivalent("x+1=x+1", "x+1=x+2")


def test_errors():
    with pytest.raises(ValueError):
        equivalent("x=1", "x+1")
    with pytest.raises(ValueError):
        equivalent("y=1", "x=1")
    with pytest.raises(ValueError):
        equivalent("x=1=2", "x=1")
    with pytest.raises(ValueError):
        equivalent("x/x=1", "x=1")


def test_cli(tmp_path, capsys):
    f = tmp_path / "w.txt"
    f.write_text("2x+6=14\n2x=8\nx=5\n")
    assert main([str(f)]) == 1
    out = capsys.readouterr().out
    assert "Line 2: ok" in out and "Line 3: NOT" in out
