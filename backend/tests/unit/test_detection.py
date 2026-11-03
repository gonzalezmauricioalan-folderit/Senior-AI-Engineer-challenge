from datetime import date, timedelta

import pytest

from app.domain.detection import Status, evaluate, weekday_usuals

S2_HISTORY = [20, 22, 18, 21, 19, 20, 23, 17]


def test_s2_numbers():
    ev = evaluate(21, S2_HISTORY)
    # median 20; MAD 1.5 -> 1.4826*1.5 = 2.22 < sqrt(20) = 4.47, so the sqrt floor sets the spread
    assert ev.usual == 20.0
    assert ev.lower == pytest.approx(20 - 2.5 * 20**0.5)  # 8.82
    assert ev.upper == pytest.approx(31.18, abs=0.01)
    assert ev.lower == pytest.approx(8.82, abs=0.01)
    assert ev.pct_vs_usual == pytest.approx(0.05)
    assert ev.status is Status.NORMAL
    assert not ev.low_volume
    assert ev.history_weeks == 8


def test_s3_lower_and_higher():
    assert evaluate(5, S2_HISTORY).status is Status.LOWER
    assert evaluate(5, S2_HISTORY).pct_vs_usual == pytest.approx(-0.75)
    assert evaluate(40, S2_HISTORY).status is Status.HIGHER


def test_history_below_and_at_minimum():
    short = evaluate(5, [20, 20, 20])
    assert short.status is Status.NOT_ENOUGH
    assert (short.usual, short.lower, short.upper, short.pct_vs_usual) == (None, None, None, None)
    assert short.history_weeks == 3 and short.total == 5 and not short.low_volume
    four = evaluate(5, [20] * 4)  # exactly MIN_HISTORY: evaluated
    assert four.status is Status.LOWER and four.history_weeks == 4


def test_usual_zero():
    zeros = [0] * 8
    assert evaluate(3, zeros).status is Status.HIGHER  # no pct, but value > 0 and diff >= MIN_ABS
    assert evaluate(3, zeros).pct_vs_usual is None
    assert evaluate(2, zeros).status is Status.NORMAL  # diff < MIN_ABS
    assert evaluate(0, zeros).status is Status.NORMAL


def test_guards_and_robustness():
    assert evaluate(236, [200] * 8).status is Status.NORMAL  # above upper 235.4 but only +18%
    assert evaluate(241, [200] * 8).status is Status.HIGHER
    ev = evaluate(0, [5] * 8)
    assert ev.status is Status.NORMAL and ev.lower == 0.0 and ev.low_volume  # diff 5 but lower bound is 0
    assert evaluate(3, [1, 1, 1, 1, 0, 0, 0, 0]).status is Status.NORMAL  # usual 0.5, diff 2.5 < 3
    spike = [20, 20, 20, 300, 20, 20, 20, 20]
    assert evaluate(20, spike).status is Status.NORMAL and evaluate(5, spike).status is Status.LOWER


def test_weekday_usuals():
    w1, w2, w3 = date(2026, 6, 1), date(2026, 6, 8), date(2026, 6, 15)
    daily = {w1: 1, w2: 5, w3: 3, w1 + timedelta(days=6): 10}  # Mondays 1,5,3; Sundays 10,0,0
    usuals = weekday_usuals([w1, w2, w3], daily)
    assert len(usuals) == 7
    assert usuals[0] == 3.0 and usuals[6] == 0.0 and usuals[2] == 0.0
    assert weekday_usuals([], daily) == [None] * 7
