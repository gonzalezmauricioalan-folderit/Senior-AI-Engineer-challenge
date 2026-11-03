"""Is this week normal? Robust median/MAD band around the usual weekly volume (PLAN.md section 2: Detection).

The pseudocode in PLAN.md is authoritative; constants live here. Values are returned unrounded:
rounding is the service's job.

How evaluate(value, history) decides:

    fewer than MIN_HISTORY (4) history weeks? ── yes ──▶ NOT_ENOUGH (usual/band/pct = None)
                     │ no
                     ▼
    usual  = median(history)                  a single spike week can't move it
    MAD    = median(|week − usual|)           the "typical wobble"
    spread = max(1.4826 · MAD, √usual)        never narrower than chance (Poisson noise)
    band   = [max(0, usual − K·spread), usual + K·spread]       K = 2.5
                     │
                     ▼
    flag only if ALL of:  a) value outside the band
                          b) |value − usual| ≥ MIN_ABS (3)
                          c) |pct| ≥ MIN_PCT (20%)   (if usual == 0: value > 0)
                     │
          flagged ───┴─── not flagged
             ▼                 ▼
    HIGHER if value > usual   NORMAL
    else LOWER
    (separately: low_volume = usual ≤ LOW_VOLUME_USUAL (6), a UI warning only)

Example 1, a typical account (scenarios S2/S3).
History 20 22 18 21 19 20 23 17: usual 20, MAD 1.5 (×1.4826 = 2.2) < √20 = 4.47, so spread 4.47
and band 8.8 – 31.2.

       0    5         8.8              20  21           31.2         40
       ├────●─────────┼────────────────●───●────────────┼────────────●───▶ events
            5: LOWER −75%                  21: NORMAL +5%            40: HIGHER +100%

Example 2, a one-off spike in the history (scenario R1).
History 20 20 20 300 20 20 20 20: the mean would be 55 and a drop to 5 might pass as normal.
The median is 20 and MAD is 0, so the √20 floor gives the same band as Example 1 (8.8 – 31.2):
week 20 is NORMAL and week 5 is LOWER. This is why the seed's 2026-06-03 spike (account 6) doesn't
distort the weeks after it.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from math import sqrt
from statistics import median

K = 2.5  # band half-width, in "spreads"
N_WEEKS = 8  # history window, in weeks
MIN_HISTORY = 4  # fewer history weeks than this -> no verdict
MIN_ABS = 3  # ignore deviations smaller than this many events
MIN_PCT = 0.20  # ignore deviations smaller than 20% of usual
LOW_VOLUME_USUAL = 6  # usual <= this -> the UI warns that percentages are noisy
MAD_SCALE = 1.4826  # makes MAD comparable to a standard deviation for roughly normal data


class Status(StrEnum):
    NORMAL = "normal"
    LOWER = "lower_than_usual"
    HIGHER = "higher_than_usual"
    NOT_ENOUGH = "not_enough_history"


@dataclass(frozen=True)
class Evaluation:
    total: int
    usual: float | None
    lower: float | None
    upper: float | None
    pct_vs_usual: float | None
    status: Status
    low_volume: bool
    history_weeks: int


def evaluate(value: int, history: Sequence[int]) -> Evaluation:
    """Compare a week's total with the counts of its history weeks (the week itself is not in them)."""
    n = len(history)
    if n < MIN_HISTORY:
        return Evaluation(value, None, None, None, None, Status.NOT_ENOUGH, False, n)

    # Median, not mean: a single spike week in the history must not inflate the baseline (scenario R1).
    usual = float(median(history))
    mad = median(abs(x - usual) for x in history)
    # Floor of sqrt(usual): for steady series MAD can be 0, which would make any +1 look anomalous.
    # sqrt(usual) is the Poisson noise of a count, so the band never gets narrower than chance alone.
    spread = max(MAD_SCALE * mad, sqrt(usual))
    lower = max(0.0, usual - K * spread)  # counts can't be negative
    upper = usual + K * spread

    diff = value - usual
    pct = diff / usual if usual > 0 else None  # a percentage of zero is undefined

    outside_band = value < lower or value > upper
    # Second and third guards stop tiny absolute or relative changes from being flagged.
    # When usual == 0 there is no percentage, so the pct guard is replaced by "there is activity"
    # (value > 0); the MIN_ABS guard still requires at least MIN_ABS events (scenarios B3/B4).
    pct_ok = abs(pct) >= MIN_PCT if pct is not None else value > 0
    flagged = outside_band and abs(diff) >= MIN_ABS and pct_ok

    if not flagged:
        status = Status.NORMAL
    else:
        status = Status.HIGHER if diff > 0 else Status.LOWER

    return Evaluation(value, usual, lower, upper, pct, status, usual <= LOW_VOLUME_USUAL, n)


def weekday_usuals(history_weeks: Sequence[date], daily: Mapping[date, int]) -> list[float | None]:
    """Usual count for each weekday (Mon..Sun): median over the history weeks (section 2: Daily context).

    Context for the chart only; days never get a status. Returns Nones when there is no history
    (the service also passes no weeks when the account summary is not_enough_history).
    """
    if not history_weeks:
        return [None] * 7
    return [float(median(daily.get(w + timedelta(days=i), 0) for w in history_weeks)) for i in range(7)]
