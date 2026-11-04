import { Bar, CartesianGrid, ComposedChart, Line, ResponsiveContainer, XAxis, YAxis } from "recharts";
import type { Day } from "../api/types";

interface Props {
  days: Day[];
}

const HEIGHT = 240;
// ResponsiveContainer renders nothing until it has measured a size, and jsdom has no layout (0x0).
// Giving it an initial size makes the chart render in tests and avoids an empty first paint in browsers;
// the real measurement replaces it as soon as ResizeObserver reports.
const INITIAL = { width: 640, height: HEIGHT };

export default function DailyChart({ days }: Props) {
  // The API's own order and numbers; only the field names are adapted for Recharts.
  const data = days.map((d) => ({ weekday: d.weekday, total: d.total, usual: d.usual }));
  const chart = (
    <ComposedChart data={data} accessibilityLayer>
      <CartesianGrid vertical={false} stroke="var(--color-border)" />
      <XAxis dataKey="weekday" />
      <YAxis allowDecimals={false} width={32} />
      <Bar dataKey="total" name="Events" fill="var(--color-bar)" isAnimationActive={false} />
      {/* Dots only: usual is a per-day reference mark, not a trend line (3.7). */}
      <Line dataKey="usual" name="Usual" stroke="none" dot={{ r: 4, fill: "var(--color-usual)", stroke: "none" }} activeDot={false} isAnimationActive={false} />
    </ComposedChart>
  );

  return (
    <section className="daily-chart" aria-label="This week by day">
      <h2>This week by day</h2>
      <div role="img" aria-label="Events per day this week, with the usual value for each day">
        <ResponsiveContainer width="100%" height={HEIGHT} initialDimension={INITIAL}>
          {chart}
        </ResponsiveContainer>
      </div>
      {/* Text alternative for the chart: the same 7 numbers, readable by screen readers. */}
      <ul className="visually-hidden" aria-label="Daily totals">
        {days.map((d) => (
          <li key={d.date}>
            {d.weekday}: {d.total} events, usual {d.usual === null ? "—" : d.usual}
          </li>
        ))}
      </ul>
    </section>
  );
}
