# Detection tuning (DASH-247)

This doc tunes the parameters of the detection method chosen in `PLAN_first_iteration.md` ("Detection method — DECIDED"). Every number here comes from `analysis/tune_detection.py`, which is read-only against the seeded Postgres. To reproduce:

```bash
backend/.venv/bin/python analysis/tune_detection.py     # DATABASE_URL defaults to the compose DB
```

## 1. Recommendation

**k = 2.5, N = 8 weeks, min_abs = 3 events, min_pct = 20%.** One setting for both levels.

| | Evaluated weeks | Lower | Higher | Total flagged | Pure-noise rate (Poisson null) |
|---|---|---|---|---|---|
| Account | 399 | 0.8% | 2.3% | **3.0%** (12 weeks) | 1.8% |
| Location | 1,449 | 0.1% | 2.5% | **2.6%** (1.5% without account 6's spike week) | 2.1% |

- **Spike check passes.** Account 6's week of 2026-06-01 (880 events, usual 66) is flagged `higher_than_usual`, and so are **15 of its 15 locations**. This holds at every point of the grid. The 7 weeks after the spike are all `normal`, and their bands look like the pre-spike ones.
- **Why k = 2.5.** At k = 2 the account flag rate (6.0%) is barely above what pure count noise gives (5.2%), so most of those flags would be false alarms. A 15-site account would show about one flagged site every week. At k = 3 there are **no** `lower_than_usual` account weeks at all. That misses drops a customer would care about, such as account 2 at 18 vs a usual 32.5 (−45%). At k = 2.5 the account flags run at 1.7× the noise rate, and the flagged weeks are deviations of 30–94%.
- **Why N = 8.** Its noise rate (1.8%) is close to N = 12 (1.5%) and well below N = 4 (2.6%). One outlier is 1 of 8 weeks, so the median and MAD absorb it. With N = 4 the spike inflates the band to an upper bound of about 170 for a month. N = 8 gives 17 full-window weeks vs 13 for N = 12, adapts to level changes within two months, and matches the wireframe's "vs. previous 8 weeks".
- **Why these floors, given they change nothing here.** None of the floors in the grid changes a single verdict at k ≥ 2.5, at either level (see §3.2). The `√median` term in the spread already implies them. (3, 20%) is kept as cheap insurance for data outside the seed's range. It never flags a difference of 1–2 events, and it never flags a change below 20% on a large account where `√median` makes the band narrow in percent terms. There's no evidence for different floors per level.
- **Below the 5–10% intuition, on purpose.** On this seed, week-to-week variation is almost pure Poisson noise (Data_integrity §14). A 5–10% flag rate would mostly be noise. 3% means roughly one flagged week per account per 8 months, and each flag is a large move.

**Trade-offs.**
- Location-level flags are mostly noise, because the real rate is at or below the null rate. Location rows are useful for "which site drove the account flag?", not as standalone alerts.
- Small sites are still flagged about 3.5× more often than larger ones (3.3% vs 0.9%, outside the spike week). The floors don't change that; only k does.
- `lower_than_usual` is structurally almost impossible at location level. When the usual is ≤ k² ≈ 6, the lower bound clamps to 0, so even a week with **zero** events reads `normal`. See Limitations.

## 2. Method (as implemented)

**Data.** `activity_events` minus the 12 exact duplicates: same `account_id, location, event_type, occurred_at, duration_seconds, outcome`, keeping the lowest `id`. That leaves 12,626 → 12,614 rows. Nothing else is removed, and account 6's spike stays in.

**Weeks.** `occurred_at` (naive UTC) is tagged UTC and converted with `zoneinfo.ZoneInfo(account.timezone)`. Week = the local Monday, covering Mon–Sun. The dataset's first and last local weeks (one day each) are dropped. That leaves **25 complete weeks, 2026-02-02 to 2026-07-20, for every timezone**.

**Series.** There is one series per account (its weekly total) and one per account+location: 19 + 69 = 88 series. A series starts at the first complete week that has an event and ends at the last complete week. Weeks without events inside that range count as 0. Every seed series turns out to cover all 25 weeks. Account 20 has no events and so no series.

**Baseline.** For the week at index *i*, `history` = the values of weeks *i−N … i−1* of the same series. The evaluated week is never included. If `len(history) < 4` → `not_enough_history`. If 4 ≤ len < N, the available weeks are used.

**Band.**
```
usual  = median(history)
MAD    = median(|x − usual| for x in history)
spread = max(1.4826 · MAD, √usual)
lower  = max(0, usual − k · spread)
upper  = usual + k · spread
```

**Flag.**
```
diff = value − usual
pct  = diff / usual                     (None when usual = 0)
flag if  (value < lower or value > upper)
     and |diff| ≥ min_abs
     and (|pct| ≥ min_pct   if usual > 0
          else value > 0)               # usual = 0: relative change treated as infinite
status = higher_than_usual if diff > 0 else lower_than_usual; otherwise normal
```

**When usual = 0.** `spread` reduces to `1.4826·MAD`. If the history is all zeros, the band is [0, 0]. The API returns `pct_vs_usual` as `null`, and the percent floor counts as passed for any value > 0, so the band and `min_abs` decide. With (3, 20%), a site with all-zero history is `normal` at 1–2 events and `higher_than_usual` at ≥ 3. A value of 0 can never be flagged lower, because the test is strictly `value < lower`. The script includes a synthetic check of this; the seed itself never produces a zero median.

## 3. Grid results

### 3.1 Evaluable weeks per N (each series has 25 complete weeks)

| N | `not_enough_history` weeks | Weeks evaluated (history ≥ 4) | Of which a full N-week window |
|---|---|---|---|
| 4 | 4 | 21 | 21 |
| 8 | 4 | 21 | 17 |
| 12 | 4 | 21 | 13 |

Because of the 4-week minimum, every N evaluates the same 21 weeks per series: 399 account-weeks and 1,449 location-weeks. N only changes how much history the early weeks get. Rates computed only on weeks 13–25, where every N has a full window, differ from the overall rates by less than 1 point.

### 3.2 Flag rates (% of evaluated weeks, lower / higher / **total**)

The floors don't change any account-level number. At location level they change only the k = 2 rows, and only for (5, 25%). So the table collapses the floors.

| k | N | Account low / high / **total** | Location low / high / **total**, floors (0,0)–(3,20%) | Location total, floors (5, 25%) |
|---|---|---|---|---|
| 2.0 | 4 | 4.0 / 4.8 / **8.8** | 1.7 / 6.4 / **8.1** | 7.4 |
| 2.0 | 8 | 2.8 / 3.3 / **6.0** | 1.0 / 5.2 / **6.2** | 5.8 |
| 2.0 | 12 | 2.5 / 3.0 / **5.5** | 1.0 / 5.1 / **6.1** | 5.9 |
| 2.5 | 4 | 1.5 / 2.5 / **4.0** | 0.1 / 3.3 / **3.5** | 3.3 |
| **2.5** | **8** | **0.8 / 2.3 / 3.0** | **0.1 / 2.5 / 2.6** | 2.6 |
| 2.5 | 12 | 0.8 / 1.8 / **2.5** | 0.1 / 2.6 / **2.6** | 2.6 |
| 3.0 | 4 | 0.0 / 1.0 / **1.0** | 0.0 / 2.1 / **2.1** | 2.1 |
| 3.0 | 8 | 0.0 / 1.3 / **1.3** | 0.0 / 1.4 / **1.4** | 1.4 |
| 3.0 | 12 | 0.0 / 1.0 / **1.0** | 0.0 / 1.6 / **1.6** | 1.6 |
| *mean ± 2.5·std* | *8* | *2.0 / 2.5 / 4.5* | *1.4 / 4.3 / 5.7* | — |

**Why the floors are inert.** The half-width of the band is at least `k·√usual`. So any value outside the band already has `|diff| > k·√usual` and `|pct| > k/√usual`. The `min_abs` floor can only bind when `usual < (min_abs/k)²`. The `min_pct` floor can only bind when `usual > (k/min_pct)²`. For k = 2.5 with (3, 20%), that means usual < 1.4 or usual > 156. The seed's baseline medians sit between about 2.5 (small sites) and 80 (account 6), so neither floor ever binds. The only floor in the grid that bites is min_abs = 5 at k = 2, because (5/2)² = 6.25 covers the small sites. The script also confirms there are 0 location rows that fall outside the band but are kept `normal` by a floor under the recommended setting.

### 3.3 How much is noise? (Poisson null)

Each series is replaced by Poisson draws at its own mean, with the same length and no anomalies (30 replicates, seed 247), and then run through the same method.

| k | N | Null account % | Real account % | Null location % | Real location % (no A6 spike week) |
|---|---|---|---|---|---|
| 2.0 | 8 | 5.2 | 6.0 | 5.8 | 5.2 |
| 2.5 | 4 | 2.6 | 4.0 | 3.0 | 2.4 |
| **2.5** | **8** | **1.8** | **3.0** | **2.1** | **1.5** |
| 2.5 | 12 | 1.5 | 2.5 | 1.9 | 1.6 |
| 3.0 | 8 | 0.6 | 1.3 | 0.9 | 0.4 |

At account level there's real excess over noise at every k. At location level, outside the spike week, the real rate is at or below the noise rate. Many locations are under-dispersed (dispersion < 1), so at that level the method flags noise, if anything.

## 4. Sanity checks (recommended setting unless stated)

**(a) Account 6 spike, week of 2026-06-01 (America/New_York).** The week is flagged `higher_than_usual` at account level, 880 events vs usual 66 with band 27–105. **15/15 locations** are also flagged higher, each with 49–70 events vs a usual of 2.5–5. This holds for all 36 grid points and for mean/std.

**(b) The weeks after the spike.** Account 6, k = 2.5, N = 8:

| Week | Value | MAD: usual, band → status | mean/std: usual, band → status |
|---|---|---|---|
| 05-25 | 53 | 72, 39–105 → normal | 71, 44–98 → normal |
| **06-01** | **880** | 66, 27–105 → **higher** | 68, 39–97 → **higher** |
| 06-08 | 102 | 66, 23–109 → normal | 168, **0–888** → normal |
| 06-15 | 59 | 73, 29–118 → normal | 174, 0–888 → normal |
| 06-29 | 69 | 72, 29–115 → normal | 172, 0–888 → normal |
| 07-20 | 87 | 72.5, 11–134 → normal | 171, 0–888 → normal |

The MAD band after the spike is close to the one before it. Under mean/std, "usual" jumps to about 170 and the band to 0–888 for the next 8 weeks. Any week from 0 to 888 events would read `normal`, and a site or account going completely dark could not be flagged. The flag counts after the spike happen to match (0 at account level for both, 2 vs 0 of 105 location-weeks). The difference is what each method *can* detect. The 2 location flags under MAD are Sites C and J at 11 events in 06-08, a week when the account itself was 102, its highest non-spike week. Over the whole dataset mean/std also flags more ordinary weeks (4.5% / 5.7%), because a sample std over 8 small counts is noisy and sometimes tiny. That's the second reason MAD + √median won.

**(c) Small-volume locations (baseline usual ≤ 5; 26% of location-weeks).**

| Setting (N = 8) | Small: flag rate | Large: flag rate | Small, without A6 spike week | Large, without A6 spike week | Small share of all location flags |
|---|---|---|---|---|---|
| k 2.0, floors (0,0)–(3,20%) | 9.0% | 5.2% | 5.5% | 5.1% | 38% |
| k 2.0, floors (5, 25%) | 7.4% | 5.2% | 3.8% | 5.1% | 33% |
| **k 2.5, any floor** | 6.9% | 1.0% | **3.3%** | **0.9%** | 70% (about 57% without the spike week) |
| k 3.0, any floor | 4.7% | 0.3% | 1.1% | 0.2% | 86% |

14 of account 6's 15 sites are small, so the spike week inflates the "small" share. Even without that week, small sites are flagged about 3.5× more often at k ≥ 2.5. The cause is the right skew of small Poisson counts: a site with usual 4 hits 10–11 more often than a symmetric √-band expects, while the lower side is clamped at 0. **The floors in the grid don't stop small sites from dominating.** Only min_abs = 5 at k = 2 helps, and k = 2 is rejected for its noise rate anyway.

**(d) Empty and short history.**
- Account 20 has no events, so it has no series. All 25 of its weeks → `not_enough_history`.
- The first 4 weeks of every series (352 rows) → `not_enough_history`.
- The seed has no location that starts mid-range (Data_integrity 12b), so short-history locations are covered by a synthetic check in the script. A site whose first 4 weeks are 3, 4, 2, 5 shows `not_enough_history` for weeks 1–4. In week 5 it is evaluated on 4 weeks (usual 3.5, band 0–8.2), and a value of 9 is flagged higher.

## 5. Example rows (recommended setting)

| Account | Location | Week | Value | Usual | Band | vs usual | Status |
|---|---|---|---|---|---|---|---|
| 6 Metro Collision | (account) | 2026-06-01 | 880 | 66 | 27.1–104.9 | +1233% | higher_than_usual |
| 6 Metro Collision | Site A | 2026-06-01 | 49 | 4.5 | 0.0–10.1 | +989% | higher_than_usual |
| 6 Metro Collision | (account) | 2026-06-08 | 102 | 66 | 23.4–108.6 | +55% | normal (inside band) |
| 2 | (account) | 2026-07-06 | 18 | 32.5 | 18.2–46.8 | −45% | lower_than_usual |
| 12 | (account) | 2026-03-02 | 40 | 62.5 | 42.7–82.3 | −36% | lower_than_usual |
| 6 | Site G | 2026-04-27 | 6 | 2.5 | 0.0–8.1 | +140% | normal (small count, inside band) |
| 1 | (account) | 2026-02-02 | 43 | — | — | — | not_enough_history (0 prior weeks) |
| 20 Quiet Harbor Spa | (account) | any | 0 | — | — | — | not_enough_history (no events) |

These are all 12 flagged account-weeks:
- Account 5: 03-02, 03-09, 05-11, 07-06, all higher (+49% to +74%).
- Account 2: 07-06, lower.
- Account 3: 03-09, higher.
- Account 4: 04-06, higher.
- Account 6: 04-13 lower (−30%) and the 06-01 spike.
- Account 12: 03-02, lower.
- Account 14: 03-02, higher.
- Account 15: 06-01, higher (+94%). This is the same week as account 6's spike, though account 15 is in Phoenix. It may be a second planted anomaly worth asking about.

## 6. Most-flagged locations (recommended setting)

43 locations are never flagged, 17 once, 7 twice and 2 three times. Each count includes the spike week for account 6's sites.

| Location | Flagged / evaluated | Weeks flagged | Median/week | Read |
|---|---|---|---|---|
| 6 Site B | 3/21 | 03-09: 8, 03-30: 10, 06-01: 65 | 4 | Spike + 2 small-count highs → mostly noise |
| 6 Site M | 3/21 | 03-09: 8, 03-16: 9, 06-01: 50 | 4 | Spike + 2 small-count highs → noise |
| 1 Site F | 2/21 | 04-06: 14 (+), 06-01: 2 (−) | 8 | The only `lower` location flag in the dataset; plausible single-week dips, weak |
| 5 Site B | 2/21 | 05-11: 13, 07-06: 14 | 6 | **Signal**: both weeks are also account 5's flagged weeks, so this site helps explain them |
| 6 Site C | 2/21 | 06-01: 67, 06-08: 11 | 4 | Spike + the high week right after it (account at 102) → plausibly real |

Outside the spike week, at most 2 flags per location in 21 weeks. At the null rate of 2.1% per location-week, about 5 of 69 locations would reach ≥ 2 flags by chance (binomial, 21 weeks), and 5 do (6 Site B, 6 Site M, 1 Site F, 5 Site B and 18 Site D, a small site at 10 vs usual 4 twice). So apart from the spike and account 5's sites, the location rankings show noise. The UI should frame location rows as context for the account verdict.

## 7. Limitations

- **No seasonality.** 25 weeks of history can't show annual patterns, and holiday weeks would be flagged. The previous-N-weeks baseline only adapts to slow level changes (seed ratios 0.89–1.18).
- **Little history.** Each series gets only 21 evaluated weeks, and 17 of those have a full 8-week window. The rates above have wide uncertainty: one flagged account-week moves the account rate by 0.25 points.
- **Small counts.** Location medians are 4–11 per week, so a ±50% week is normal at a small site, and its flags are mostly noise. The `lower_than_usual` verdict is effectively unreachable when usual ≤ k² (≈ 6 at k = 2.5), because the lower bound clamps to 0 and `0 < 0` is false. A site that drops to zero events would read `normal`. If product cares about sites "going dark", that needs a separate rule; it's an open question, not covered by this tuning.
- **Floors untested in practice.** The seed never reaches the volumes where the floors bind (usual < 1.4 or > 156 at k = 2.5). The (3, 20%) choice is a product judgment, not a fitted value.
- **Synthetic data.** The seed is near-Poisson apart from a few planted events, so real customers with more over-dispersion would flag more often at the same k. Re-run the script on production data before calling the parameters final.
