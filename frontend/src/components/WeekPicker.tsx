import { addDays, tzAbbreviation, weekLabel } from "../format";

interface Props {
  weekStart: string;
  /** The account's `latest_complete_week`: ▶ is disabled once we are on it. */
  latestWeek: string;
  timezone: string;
  onChange: (weekStart: string) => void;
}

export default function WeekPicker({ weekStart, latestWeek, timezone, onChange }: Props) {
  return (
    <div className="picker-row">
      <span id="week-label">Week</span>
      <button type="button" aria-label="Previous week" onClick={() => onChange(addDays(weekStart, -7))}>
        ◀
      </button>
      <span aria-labelledby="week-label" data-testid="week-range">
        {weekLabel(weekStart)}
      </span>
      <button
        type="button"
        aria-label="Next week"
        disabled={weekStart >= latestWeek}
        onClick={() => onChange(addDays(weekStart, 7))}
      >
        ▶
      </button>
      <span className="muted">({tzAbbreviation(timezone, weekStart)})</span>
    </div>
  );
}
