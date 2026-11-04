/*
 * Formatting and date helpers (PLAN.md 3.7).
 *
 * API dates are "YYYY-MM-DD" strings, not instants. Parsing them with the local timezone would
 * shift the day for anyone west of UTC, so every date goes through UTC.
 *
 *   "2026-07-20" --Date.UTC(y, m-1, d)--> epoch ms --(+7 days | Intl with timeZone "UTC")--> string
 *
 *   formatPct(p):  null -> "—"
 *                  else r = Math.round(p * 100)
 *                       r > 0 -> "+r%"   r < 0 -> "−|r|%" (U+2212)   r = 0 -> "0%"
 *
 * Worked example (S3a, PLAN.md section 4): pct_vs_usual = -0.75 -> "−75%".
 */

const DAY_MS = 24 * 60 * 60 * 1000;

function parseIso(iso: string): number {
  const [y, m, d] = iso.split("-").map(Number);
  return Date.UTC(y ?? 0, (m ?? 1) - 1, d ?? 1);
}

function toIso(ms: number): string {
  return new Date(ms).toISOString().slice(0, 10);
}

/** `iso` plus `days` (may be negative), as "YYYY-MM-DD". */
export function addDays(iso: string, days: number): string {
  return toIso(parseIso(iso) + days * DAY_MS);
}

export function isMonday(iso: string): boolean {
  return new Date(parseIso(iso)).getUTCDay() === 1;
}

/** "−32%" / "+5%" / "0%"; the minus is U+2212 so it lines up with the plus. `null` -> "—". */
export function formatPct(pct: number | null): string {
  if (pct === null) return "—";
  const rounded = Math.round(pct * 100);
  if (rounded > 0) return `+${rounded}%`;
  if (rounded < 0) return `−${Math.abs(rounded)}%`;
  return "0%";
}

/** Rounded integer, or "—" for `null`. */
export function formatNumber(value: number | null): string {
  return value === null ? "—" : String(Math.round(value));
}

const utcFormat = (options: Intl.DateTimeFormatOptions) =>
  new Intl.DateTimeFormat("en-US", { ...options, timeZone: "UTC" });

/** "Jul 20 – Jul 26, 2026" for the week starting at `weekStart` (a Monday). */
export function weekLabel(weekStart: string): string {
  const start = parseIso(weekStart);
  const end = start + 6 * DAY_MS;
  const sameYear = new Date(start).getUTCFullYear() === new Date(end).getUTCFullYear();
  const startText = utcFormat(sameYear ? { month: "short", day: "numeric" } : { month: "short", day: "numeric", year: "numeric" }).format(start);
  const endText = utcFormat({ month: "short", day: "numeric", year: "numeric" }).format(end);
  return `${startText} – ${endText}`;
}

/** Short zone name ("CDT", "MST", "UTC") for `timeZone` on `isoDate`, so DST is right for that week. */
export function tzAbbreviation(timeZone: string, isoDate: string): string {
  // Noon UTC keeps the date stable in every zone from -12 to +12.
  const instant = parseIso(isoDate) + 12 * 60 * 60 * 1000;
  const parts = new Intl.DateTimeFormat("en-US", { timeZone, timeZoneName: "short" }).formatToParts(instant);
  return parts.find((part) => part.type === "timeZoneName")?.value ?? timeZone;
}

/** "1 event" / "0 events" / "2 events". */
export function formatEvents(count: number): string {
  return `${count} ${count === 1 ? "event" : "events"}`;
}
