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
