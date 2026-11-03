"""Tune the "is this week normal?" detection parameters (DASH-247).

Standalone and read-only. Run from the repo root:

    backend/.venv/bin/python analysis/tune_detection.py

Reads DATABASE_URL (default: the docker-compose Postgres). Prints the tables
that feed Detection_tuning.md. Fixed decisions implemented here:

* Data: activity_events minus the 12 exact duplicates (all columns but id equal;
  keep the lowest id). Nothing else is removed.
* Metric: total events per Mon-Sun week in the account's local time. UTC is
  converted with zoneinfo. The dataset's first and last local weeks are partial
  and dropped. Missing weeks inside a series' active range count as 0.
* Levels: account (its weekly total) and account+location.
* Baseline: the previous N complete weeks (never the evaluated week); < 4 prior
  weeks -> not_enough_history; 4 <= history < N -> use what is there.
* Band: usual = median; spread = max(1.4826*MAD, sqrt(median));
  lower = max(0, median - k*spread); upper = median + k*spread.
* Flag only if outside [lower, upper] AND |v - median| >= min_abs AND
  |v - median| / median >= min_pct. Median = 0: pct is undefined (reported as
  None); a value > 0 counts as passing the pct floor (infinite relative change),
  so only the band and min_abs decide. Value 0 with median 0 is normal.
"""
from __future__ import annotations

import math
import os
import random
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg://relay:relay@localhost:5432/relay")

MIN_HISTORY = 4
K_GRID = (2.0, 2.5, 3.0)
N_GRID = (4, 8, 12)
FLOOR_GRID = ((0, 0.0), (2, 0.15), (3, 0.20), (5, 0.25))
RECOMMENDED = dict(k=2.5, n=8, min_abs=3, min_pct=0.20)
NULL_REPLICATES = 30
NULL_SEED = 247

SPIKE_ACCOUNT = 6
SPIKE_DAY = date(2026, 6, 3)  # Wednesday, local
SMALL_MEDIAN = 5

DEDUP_SQL = text(
    """
    SELECT e.account_id, e.location, e.occurred_at
    FROM (
        SELECT *, row_number() OVER (
                   PARTITION BY account_id, location, event_type, occurred_at,
                                duration_seconds, outcome
                   ORDER BY id) AS rn
        FROM activity_events
    ) e
    WHERE e.rn = 1
    """
)


def week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


# ---------------------------------------------------------------- data loading
def load():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SET TRANSACTION READ ONLY"))
        accounts = {r.id: (r.name, r.timezone) for r in conn.execute(text("SELECT id, name, timezone FROM accounts"))}
        raw = conn.execute(text("SELECT count(*) FROM activity_events")).scalar_one()
        rows = conn.execute(DEDUP_SQL).all()
    return accounts, raw, rows


def build_series(accounts, rows):
    """Return {key: [(week_start, count), ...]} for account keys (acc, None) and
    location keys (acc, loc), restricted to complete local weeks, zero-filled
    from the series' first complete week with an event to the last complete week."""
    utc_min = min(r.occurred_at for r in rows).replace(tzinfo=timezone.utc)
    utc_max = max(r.occurred_at for r in rows).replace(tzinfo=timezone.utc)

    complete = {}  # account -> list of complete week starts
    for acc, (_, tz) in accounts.items():
        z = ZoneInfo(tz)
        first = week_start(utc_min.astimezone(z).date()) + timedelta(days=7)
        last = week_start(utc_max.astimezone(z).date()) - timedelta(days=7)
        weeks, w = [], first
        while w <= last:
            weeks.append(w)
            w += timedelta(days=7)
        complete[acc] = weeks

    counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        z = ZoneInfo(accounts[r.account_id][1])
        wk = week_start(r.occurred_at.replace(tzinfo=timezone.utc).astimezone(z).date())
        counts[(r.account_id, None)][wk] += 1
        counts[(r.account_id, r.location)][wk] += 1

    series = {}
    for key, c in counts.items():
        weeks = complete[key[0]]
        active = [w for w in weeks if c.get(w, 0) > 0]
        if not active:
            continue
        series[key] = [(w, c.get(w, 0)) for w in weeks if w >= active[0]]
    return series, complete


def poisson(rng, lam):
    """Knuth's method; fine for the small lambdas here (< 100)."""
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


# ------------------------------------------------------------------- detection
def band(history, k, method="mad"):
    if method == "mad":
        med = statistics.median(history)
        mad = statistics.median(abs(x - med) for x in history)
        spread = max(1.4826 * mad, math.sqrt(med))
        return med, max(0.0, med - k * spread), med + k * spread
    # comparison only: classic mean +/- k*std (sample std)
    mean = statistics.fmean(history)
    std = statistics.stdev(history)
    return mean, max(0.0, mean - k * std), mean + k * std


def classify(value, usual, lower, upper, min_abs, min_pct):
    diff = value - usual
    pct = diff / usual if usual > 0 else None
    pct_ok = abs(pct) >= min_pct if pct is not None else value > 0
    if (value < lower or value > upper) and abs(diff) >= min_abs and pct_ok:
        return ("higher_than_usual" if diff > 0 else "lower_than_usual"), pct
    return "normal", pct


def evaluate(series, k, n, min_abs, min_pct, method="mad"):
    """Yield one dict per (series, week)."""
    for key, pts in series.items():
        values = [v for _, v in pts]
        for i, (wk, v) in enumerate(pts):
            hist = values[max(0, i - n):i]
            row = dict(account=key[0], location=key[1], week=wk, value=v, history=len(hist))
            if len(hist) < MIN_HISTORY:
                row.update(status="not_enough_history", usual=None, lower=None, upper=None, pct=None)
            else:
                usual, lo, hi = band(hist, k, method)
                status, pct = classify(v, usual, lo, hi, min_abs, min_pct)
                row.update(status=status, usual=usual, lower=lo, upper=hi, pct=pct)
            yield row


def rates(rows):
    ev = [r for r in rows if r["status"] != "not_enough_history"]
    lo = sum(r["status"] == "lower_than_usual" for r in ev)
    hi = sum(r["status"] == "higher_than_usual" for r in ev)
    n = len(ev) or 1
    return len(ev), 100 * lo / n, 100 * hi / n, 100 * (lo + hi) / n


def fmt(x, d=1):
    return "-" if x is None else f"{x:.{d}f}"


# --------------------------------------------------------------------- reports
def main():
    accounts, raw, rows = load()
    series, complete = build_series(accounts, rows)
    spike_week = week_start(SPIKE_DAY)
    acc_keys = [k for k in series if k[1] is None]
    loc_keys = [k for k in series if k[1] is not None]
    print(f"raw events {raw}, after dedup {len(rows)} (removed {raw - len(rows)})")
    print(f"account series {len(acc_keys)}, location series {len(loc_keys)}")
    print(f"complete weeks per account: {sorted({len(w) for w in complete.values()})}, "
          f"{min(min(w) for w in complete.values())} .. {max(max(w) for w in complete.values())}")
    print(f"accounts without events: {sorted(set(accounts) - {k[0] for k in acc_keys})}")
    lens = sorted({len(p) for p in series.values()})
    print(f"series lengths (weeks): {lens}")

    # Evaluable weeks per N
    print("\n## Evaluable weeks per series, by N")
    print("| N | weeks not_enough_history | weeks evaluated (history >= 4) | of which full N-week window |")
    print("|---|---|---|---|")
    L = max(lens)
    for n in N_GRID:
        ev = L - MIN_HISTORY
        full = L - n
        print(f"| {n} | {MIN_HISTORY} | {ev} | {full} |")

    # Common weeks: weeks where every N in the grid has a full window
    common_from = max(N_GRID)

    def split(rows_):
        acc = [r for r in rows_ if r["location"] is None]
        loc = [r for r in rows_ if r["location"] is not None]
        return acc, loc

    def not_spike(r):
        return not (r["account"] == SPIKE_ACCOUNT and r["week"] == spike_week)

    def is_common(r):
        pts = series[(r["account"], r["location"])]
        return [w for w, _ in pts].index(r["week"]) >= common_from

    print("\n## Grid (MAD band). Rates are % of evaluated weeks: lower / higher / total")
    print("| k | N | min_abs | min_pct | account low | account high | account total | location low | location high "
          "| location total | location total (common wks) | loc small (usual<=5) | loc large | A6 spike acct | A6 spike locs higher |")
    print("|" + "---|" * 15)
    results = {}
    for k in K_GRID:
        for n in N_GRID:
            for (ma, mp) in FLOOR_GRID:
                out = list(evaluate(series, k, n, ma, mp))
                acc, loc = split(out)
                _, al, ah, at = rates(acc)
                _, ll, lh, lt = rates(loc)
                _, _, _, lct = rates([r for r in loc if is_common(r)])
                small = [r for r in loc if r["usual"] is not None and r["usual"] <= SMALL_MEDIAN]
                large = [r for r in loc if r["usual"] is not None and r["usual"] > SMALL_MEDIAN]
                sp_acc = next(r["status"] for r in acc if r["account"] == SPIKE_ACCOUNT and r["week"] == spike_week)
                sp_loc = sum(r["status"] == "higher_than_usual" for r in loc
                             if r["account"] == SPIKE_ACCOUNT and r["week"] == spike_week)
                results[(k, n, ma, mp)] = out
                print(f"| {k} | {n} | {ma} | {mp:.2f} | {al:.1f} | {ah:.1f} | {at:.1f} | {ll:.1f} | {lh:.1f} | {lt:.1f} "
                      f"| {lct:.1f} | {rates(small)[3]:.1f} | {rates(large)[3]:.1f} | {sp_acc.split('_')[0]} | {sp_loc}/15 |")

    # Small-volume share of flags
    print("\n## Small-volume locations (baseline usual <= 5): share of evaluated rows vs share of flags")
    print("| k | N | floors | small rows % | small share of loc flags % | small flag rate | large flag rate "
          "| small rate excl. A6 spike wk | large rate excl. A6 spike wk |")
    print("|---|---|---|---|---|---|---|---|---|")
    for (k, n, ma, mp), out in results.items():
        if n != RECOMMENDED["n"]:
            continue
        loc = [r for r in out if r["location"] is not None and r["usual"] is not None]
        small = [r for r in loc if r["usual"] <= SMALL_MEDIAN]
        fl = [r for r in loc if r["status"].endswith("usual")]
        fs = [r for r in fl if r["usual"] <= SMALL_MEDIAN]
        print(f"| {k} | {n} | ({ma}, {mp:.2f}) | {100*len(small)/len(loc):.1f} | {100*len(fs)/max(1,len(fl)):.1f} "
              f"| {rates(small)[3]:.1f} | {rates([r for r in loc if r['usual'] > SMALL_MEDIAN])[3]:.1f} "
              f"| {rates([r for r in small if not_spike(r)])[3]:.1f} "
              f"| {rates([r for r in loc if r['usual'] > SMALL_MEDIAN and not_spike(r)])[3]:.1f} |")

    # Account 6 around the spike: MAD vs mean/std
    rk, rn, rma, rmp = RECOMMENDED["k"], RECOMMENDED["n"], RECOMMENDED["min_abs"], RECOMMENDED["min_pct"]
    print(f"\n## Account 6 around the spike (k={rk}, N={rn}, floors=({rma}, {rmp}))")
    print("| week | value | MAD: usual | MAD: band | MAD: status | mean/std: usual | mean/std: band | mean/std: status |")
    print("|---|---|---|---|---|---|---|---|")
    mad_rows = {r["week"]: r for r in evaluate({(6, None): series[(6, None)]}, rk, rn, rma, rmp)}
    ms_rows = {r["week"]: r for r in evaluate({(6, None): series[(6, None)]}, rk, rn, rma, rmp, "meanstd")}
    for wk in sorted(mad_rows):
        if wk < spike_week - timedelta(days=14):
            continue
        a, b = mad_rows[wk], ms_rows[wk]
        print(f"| {wk} | {a['value']} | {fmt(a['usual'])} | {fmt(a['lower'])}-{fmt(a['upper'])} | {a['status']} "
              f"| {fmt(b['usual'])} | {fmt(b['lower'])}-{fmt(b['upper'])} | {b['status']} |")

    print("\n## Post-spike distortion: account 6, weeks after the spike week")
    print("| method | k | N | post-spike weeks inside window | acct flags | loc flags | median upper bound (acct) |")
    print("|---|---|---|---|---|---|---|")
    a6 = {k_: v for k_, v in series.items() if k_[0] == SPIKE_ACCOUNT}
    for method in ("mad", "meanstd"):
        for n in N_GRID:
            out = [r for r in evaluate(a6, rk, n, rma, rmp, method)
                   if spike_week < r["week"] <= spike_week + timedelta(weeks=n)]
            acc = [r for r in out if r["location"] is None]
            loc = [r for r in out if r["location"] is not None]
            ups = sorted(r["upper"] for r in acc)
            print(f"| {method} | {rk} | {n} | {len(acc)} | {sum(r['status'] != 'normal' for r in acc)} "
                  f"| {sum(r['status'] != 'normal' for r in loc)}/{len(loc)} | {statistics.median(ups):.0f} |")

    # Same comparison over the whole grid point (flag rates)
    print("\n## Mean/std comparison row (recommended k, N, floors)")
    out = list(evaluate(series, rk, rn, rma, rmp, "meanstd"))
    acc, loc = split(out)
    sp = next(r for r in acc if r["account"] == SPIKE_ACCOUNT and r["week"] == spike_week)
    print(f"account total {rates(acc)[3]:.1f}% (low {rates(acc)[1]:.1f} / high {rates(acc)[2]:.1f}); "
          f"location total {rates(loc)[3]:.1f}% (low {rates(loc)[1]:.1f} / high {rates(loc)[2]:.1f}); "
          f"spike week {sp['status']}")

    # Recommended setting: details
    rec = results[(rk, rn, rma, rmp)]
    acc, loc = split(rec)
    print(f"\n## Recommended k={rk}, N={rn}, floors=({rma}, {rmp})")
    print(f"accounts: evaluated {rates(acc)[0]}, low {rates(acc)[1]:.1f}%, high {rates(acc)[2]:.1f}%, total {rates(acc)[3]:.1f}%")
    print(f"locations: evaluated {rates(loc)[0]}, low {rates(loc)[1]:.1f}%, high {rates(loc)[2]:.1f}%, total {rates(loc)[3]:.1f}%")
    ex_spike = [r for r in loc if not (r["account"] == SPIKE_ACCOUNT and r["week"] == spike_week)]
    print(f"locations excl. A6 spike week: total {rates(ex_spike)[3]:.1f}%")
    neh = [r for r in rec if r["status"] == "not_enough_history"]
    print(f"not_enough_history rows: {len(neh)} (= first {MIN_HISTORY} weeks of each of {len(series)} series); "
          f"account 20: all {len(complete[20])} complete weeks have no series -> not_enough_history")
    per_acc = defaultdict(int)
    for r in acc:
        if r["status"].endswith("usual"):
            per_acc[r["account"]] += 1
    print("account flags per account:", dict(sorted(per_acc.items())))

    print("\n### Top flagged locations")
    print("| account | location | flagged weeks / evaluated | low | high | of which A6 spike week | median weekly | weeks flagged |")
    print("|---|---|---|---|---|---|---|---|")
    by = defaultdict(list)
    for r in loc:
        by[(r["account"], r["location"])].append(r)
    ranked = sorted(by.items(), key=lambda kv: -sum(r["status"].endswith("usual") for r in kv[1]))
    for (a, l), rs in ranked[:10]:
        fl = [r for r in rs if r["status"].endswith("usual")]
        med = statistics.median(v for _, v in series[(a, l)])
        lw = sum(r["status"] == "lower_than_usual" for r in fl)
        sp = sum(r["week"] == spike_week and a == SPIKE_ACCOUNT for r in fl)
        wks = ", ".join(f"{r['week'].strftime('%m-%d')}:{r['value']}({'-' if r['status'][0]=='l' else '+'})" for r in fl)
        n_ev = sum(r["status"] != "not_enough_history" for r in rs)
        print(f"| {a} | {l} | {len(fl)}/{n_ev} | {lw} | {len(fl)-lw} | {sp} | {med:g} | {wks} |")
    dist = defaultdict(int)
    for rs in by.values():
        dist[sum(r["status"].endswith("usual") for r in rs)] += 1
    print("locations by number of flagged weeks:", dict(sorted(dist.items())))

    print("\n### All flagged account-weeks")
    print("| account | week | value | usual | band | pct | status |")
    print("|---|---|---|---|---|---|---|")
    for r in sorted(acc, key=lambda r: (r["account"], r["week"])):
        if r["status"].endswith("usual"):
            print(f"| {r['account']} | {r['week']} | {r['value']} | {fmt(r['usual'])} | {fmt(r['lower'])}-{fmt(r['upper'])} "
                  f"| {fmt(100*r['pct'],0) if r['pct'] is not None else '-'}% | {r['status']} |")

    print("\n### Near misses at location level (outside the band but stopped by a floor)")
    stopped = 0
    for r in loc:
        if r["status"] == "normal" and r["usual"] is not None and not (r["lower"] <= r["value"] <= r["upper"]):
            stopped += 1
    print(f"location rows outside band but normal due to floors: {stopped}")

    # Poisson null: same series lengths and levels, pure count noise, no anomalies.
    print(f"\n## Poisson null ({NULL_REPLICATES} replicates; lambda = series mean excl. A6 spike week)")
    print("| k | N | null account % | real account % | null location % | real location % (excl. A6 spike wk) |")
    print("|---|---|---|---|---|---|")
    rng = random.Random(NULL_SEED)
    lam = {key: statistics.fmean(v for w, v in pts if not (key[0] == SPIKE_ACCOUNT and w == spike_week))
           for key, pts in series.items()}
    sims = []
    for _ in range(NULL_REPLICATES):
        sims.append({key: [(w, poisson(rng, lam[key])) for w, _ in pts] for key, pts in series.items()})
    for k in K_GRID:
        for n in N_GRID:
            na, nl = [], []
            for sim in sims:
                a_, l_ = split(list(evaluate(sim, k, n, rma, rmp)))
                na += a_
                nl += l_
            ra, rl = split(results[(k, n, rma, rmp)])
            print(f"| {k} | {n} | {rates(na)[3]:.1f} | {rates(ra)[3]:.1f} | {rates(nl)[3]:.1f} "
                  f"| {rates([r for r in rl if not_spike(r)])[3]:.1f} |")

    print("\n### Example rows (recommended)")
    print("| account | location | week | value | usual | band | pct | status |")
    print("|---|---|---|---|---|---|---|---|")
    picks = [(6, None, spike_week), (6, "Site A", spike_week), (6, None, spike_week + timedelta(weeks=1)),
             (2, None, date(2026, 7, 6)), (12, None, date(2026, 3, 2))]
    big_swing = max((r for r in loc if r["status"] == "normal" and r["usual"] and r["usual"] <= SMALL_MEDIAN),
                    key=lambda r: abs(r["pct"]))
    picks.append((big_swing["account"], big_swing["location"], big_swing["week"]))
    picks.append((1, "Site A", spike_week))
    for a, l, w in picks:
        r = next(r for r in rec if r["account"] == a and r["location"] == l and r["week"] == w)
        pct = f"{100 * r['pct']:+.0f}%" if r["pct"] is not None else "-"
        print(f"| {a} | {l or '(account)'} | {w} | {r['value']} | {fmt(r['usual'])} | {fmt(r['lower'])}-{fmt(r['upper'])} "
              f"| {pct} | {r['status']} |")
    first = next(r for r in rec if r["account"] == 1 and r["location"] is None)
    print(f"| 1 | (account) | {first['week']} | {first['value']} | - | - | - | {first['status']} (history {first['history']}) |")
    print(f"| 20 | (account) | any | 0 | - | - | - | not_enough_history (no events) |")

    # Synthetic check: short history and median 0
    print("\n### Synthetic checks")
    synth = {(99, "new"): [(date(2026, 7, 6) + timedelta(weeks=i), v) for i, v in enumerate([3, 4, 2, 5, 9])],
             (99, "zeros"): [(date(2026, 6, 1) + timedelta(weeks=i), v) for i, v in enumerate([0, 0, 0, 0, 0, 1, 4])]}
    for r in evaluate(synth, rk, rn, rma, rmp):
        print(r["location"], r["week"], r["value"], r["history"], r["status"], fmt(r["usual"]), fmt(r["upper"]))


if __name__ == "__main__":
    main()
