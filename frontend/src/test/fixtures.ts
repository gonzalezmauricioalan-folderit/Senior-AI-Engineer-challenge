import type { Account, WeeklyInsight } from "../api/types";

// Ordered by name, like the API. The first account is the default selection; Metro's latest week
// is earlier than Alpine's, so switching accounts visibly resets the week (F8).
export const accounts = [
  {
    id: 2,
    name: "Alpine Dental",
    industry: "dental",
    timezone: "America/Chicago",
    location_count: 1,
    latest_complete_week: "2026-07-20",
  },
  {
    id: 6,
    name: "Metro Collision Centers",
    industry: "auto",
    timezone: "America/New_York",
    location_count: 15,
    latest_complete_week: "2026-07-13",
  },
  {
    id: 20,
    name: "Quiet Harbor Spa",
    industry: "spa",
    timezone: "UTC",
    location_count: 0,
    // The real API returns the dataset-wide as-of week even for an account without events.
    latest_complete_week: "2026-07-20",
  },
] satisfies Account[];

// Empty-dataset variant: the only case where latest_complete_week is null. Tests that need it
// override the /accounts handler with this list.
export const accountsEmptyDataset = [
  {
    id: 20,
    name: "Quiet Harbor Spa",
    industry: "spa",
    timezone: "UTC",
    location_count: 0,
    latest_complete_week: null,
  },
] satisfies Account[];

// S2 (PLAN.md section 4): history [20,22,18,21,19,20,23,17], week = 21 -> usual 20.0, band 8.8-31.2, +5%, normal.
export const insightS2 = {
  account: { id: 2, name: "Alpine Dental", timezone: "America/Chicago" },
  week: { start: "2026-07-20", end: "2026-07-26" },
  baseline: { method: "median_mad", weeks_used: 8, start: "2026-05-25", end: "2026-07-19" },
  summary: { total: 21, usual: 20.0, lower: 8.8, upper: 31.2, pct_vs_usual: 0.05, status: "normal", low_volume: false },
  days: [
    { date: "2026-07-20", weekday: "Mon", total: 3, usual: 3.0 },
    { date: "2026-07-21", weekday: "Tue", total: 4, usual: 3.0 },
    { date: "2026-07-22", weekday: "Wed", total: 3, usual: 3.0 },
    { date: "2026-07-23", weekday: "Thu", total: 4, usual: 3.0 },
    { date: "2026-07-24", weekday: "Fri", total: 3, usual: 3.0 },
    { date: "2026-07-25", weekday: "Sat", total: 2, usual: 2.5 },
    { date: "2026-07-26", weekday: "Sun", total: 2, usual: 2.5 },
  ],
  locations: [
    {
      location: "Main",
      total: 21,
      usual: 20.0,
      lower: 8.8,
      upper: 31.2,
      pct_vs_usual: 0.05,
      status: "normal",
      low_volume: false,
      history_weeks: 8,
    },
  ],
  data_notes: [],
} satisfies WeeklyInsight;

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;
const DATES = ["2026-07-20", "2026-07-21", "2026-07-22", "2026-07-23", "2026-07-24", "2026-07-25", "2026-07-26"] as const;

/** Seven days from daily totals and usual values, so the scenario fixtures stay short. */
function daysOf(totals: number[], usuals: (number | null)[]): WeeklyInsight["days"] {
  return WEEKDAYS.map((weekday, i) => ({ date: DATES[i] ?? "", weekday, total: totals[i] ?? 0, usual: usuals[i] ?? null }));
}

// S1: account without events. No history, so no usual, no locations, and 7 zero days.
export const insightS1 = {
  account: { id: 20, name: "Quiet Harbor Spa", timezone: "UTC" },
  week: { start: "2026-07-20", end: "2026-07-26" },
  baseline: { method: "median_mad", weeks_used: 0, start: null, end: null },
  summary: { total: 0, usual: null, lower: null, upper: null, pct_vs_usual: null, status: "not_enough_history", low_volume: false },
  days: daysOf([0, 0, 0, 0, 0, 0, 0], [null, null, null, null, null, null, null]),
  locations: [],
  data_notes: [],
} satisfies WeeklyInsight;

// S3a: same history as S2, week = 5 -> lower_than_usual, -75%.
export const insightS3a = {
  ...insightS2,
  summary: { total: 5, usual: 20.0, lower: 8.8, upper: 31.2, pct_vs_usual: -0.75, status: "lower_than_usual", low_volume: false },
  days: daysOf([1, 1, 1, 1, 1, 0, 0], [3, 3, 3, 3, 3, 2.5, 2.5]),
  locations: [],
} satisfies WeeklyInsight;

// S3b: same history as S2, week = 40 -> higher_than_usual, +100%.
export const insightS3b = {
  ...insightS2,
  summary: { total: 40, usual: 20.0, lower: 8.8, upper: 31.2, pct_vs_usual: 1.0, status: "higher_than_usual", low_volume: false },
  days: daysOf([6, 6, 6, 6, 6, 5, 5], [3, 3, 3, 3, 3, 2.5, 2.5]),
  locations: [],
} satisfies WeeklyInsight;

// B5: history [5]*8, week = 0 -> normal (lower bound clamps at 0) and the account is low volume (F5).
export const insightLowVolume = {
  ...insightS2,
  summary: { total: 0, usual: 5.0, lower: 0.0, upper: 12.0, pct_vs_usual: -1.0, status: "normal", low_volume: true },
  days: daysOf([0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 0]),
  locations: [],
} satisfies WeeklyInsight;

// R2 + R7 notes, exactly as the backend words them (backend/app/service.py).
export const DUPLICATE_NOTE = "1 duplicate event removed from this week.";
export const UTC_NOTE =
  "This account's timezone is set to UTC, which may be a misconfiguration; days and weeks may be shifted.";
export const insightWithNotes = {
  ...insightS2,
  data_notes: [DUPLICATE_NOTE, UTC_NOTE],
} satisfies WeeklyInsight;
