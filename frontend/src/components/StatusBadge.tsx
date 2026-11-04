import type { Status } from "../api/types";

// Icon + text, never colour alone (PLAN.md 3.7). Colours are the CSS variables from styles.css.
const BADGES: Record<Status, { icon: string; text: string; color: string }> = {
  lower_than_usual: { icon: "▼", text: "Lower than usual", color: "var(--color-lower)" },
  higher_than_usual: { icon: "▲", text: "Higher than usual", color: "var(--color-higher)" },
  normal: { icon: "●", text: "Normal", color: "var(--color-normal)" },
  not_enough_history: { icon: "○", text: "Not enough history", color: "var(--color-muted)" },
};

export default function StatusBadge({ status }: { status: Status }) {
  const { icon, text, color } = BADGES[status];
  return (
    <span className="status-badge" style={{ color }}>
      {icon} {text}
    </span>
  );
}
