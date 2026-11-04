import type { Metric, WeeklyInsight } from "../api/types";
import { formatEvents, formatNumber, formatPct } from "../format";
import StatusBadge from "./StatusBadge";

interface Props {
  summary: Metric;
  baseline: WeeklyInsight["baseline"];
}

export const NOT_ENOUGH_HISTORY_COPY = "Not enough history yet — at least 4 complete weeks are needed to tell what's normal.";
export const LOW_VOLUME_COPY = "This account has low weekly volume, so results may be unreliable.";

export default function VerdictCard({ summary, baseline }: Props) {
  const { total, usual, lower, upper, pct_vs_usual, status, low_volume } = summary;
  const notEnough = status === "not_enough_history";
  // null parts print "—" (3.7); never "~null" or "NaN".
  const usualText = usual === null ? "—" : `~${formatNumber(usual)}`;
  const rangeText = lower === null || upper === null ? "—" : `${formatNumber(lower)}–${formatNumber(upper)}`;

  return (
    <section className="verdict-card" aria-label="Verdict">
      <p className="verdict-status">
        <StatusBadge status={status} />
      </p>
      {notEnough ? (
        <>
          <p>{formatEvents(total)}</p>
          <p className="muted">{NOT_ENOUGH_HISTORY_COPY}</p>
        </>
      ) : (
        <>
          <p>
            {formatEvents(total)} · usual {usualText} (range {rangeText}) · {formatPct(pct_vs_usual)}
          </p>
          <p className="muted">vs. previous {baseline.weeks_used} weeks</p>
        </>
      )}
      {low_volume && <p className="warning">{LOW_VOLUME_COPY}</p>}
    </section>
  );
}
