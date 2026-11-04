/*
 * Persisted selection (PLAN.md 3.7), key "relay.dashboard.v1".
 *
 *   loadSelection():
 *     localStorage.getItem throws? ----------------------> null
 *     JSON.parse throws? --------------------------------> null
 *     not {accountId: integer, weekStart: "YYYY-MM-DD"}? -> null
 *     else ----------------------------------------------> the stored selection
 *
 *   resolveSelection(accounts, stored):
 *     accounts empty? ------------------------------------> null
 *     stored account missing from accounts? -------------> defaults
 *     stored weekStart not a Monday? ---------------------> defaults
 *     stored weekStart > account.latest_complete_week? ---> defaults
 *     else -----------------------------------------------> stored
 *     (defaults = first account, its latest_complete_week)
 *
 *   saveSelection(sel): setItem in try/catch; failures are silent (the app works without storage).
 *
 * Worked example (F12): stored {accountId: 6, weekStart: "2026-07-21"} is a Tuesday, so
 * resolveSelection falls back to the first account and its latest week, and App then overwrites
 * the stored value with that default.
 */
import type { Account } from "./api/types";
import { isMonday } from "./format";

export const STORAGE_KEY = "relay.dashboard.v1";

export interface StoredSelection {
  accountId: number;
  weekStart: string;
}

/** `weekStart` is null for an account with no complete week (nothing to request). */
export interface Selection {
  accountId: number;
  weekStart: string | null;
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function isStoredSelection(value: unknown): value is StoredSelection {
  if (typeof value !== "object" || value === null) return false;
  const { accountId, weekStart } = value as Record<string, unknown>;
  return Number.isInteger(accountId) && typeof weekStart === "string" && ISO_DATE.test(weekStart);
}

export function loadSelection(): StoredSelection | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) return null;
    const parsed: unknown = JSON.parse(raw);
    return isStoredSelection(parsed) ? parsed : null;
  } catch {
    // Blocked storage or broken JSON: behave as if nothing was stored.
    return null;
  }
}

export function saveSelection(selection: StoredSelection): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(selection));
  } catch {
    // Storage blocked or full: the selection just won't survive a reload.
  }
}

export function defaultSelection(account: Account): Selection {
  return { accountId: account.id, weekStart: account.latest_complete_week };
}

/** Validates `stored` against the accounts the API returned; see the diagram above. */
export function resolveSelection(accounts: Account[], candidate: Selection | StoredSelection | null): Selection | null {
  const first = accounts[0];
  if (!first) return null;
  if (candidate === null) return defaultSelection(first);
  const account = accounts.find((a) => a.id === candidate.accountId);
  if (!account) return defaultSelection(first);
  const latest = account.latest_complete_week;
  if (candidate.weekStart === null) return latest === null ? { accountId: account.id, weekStart: null } : defaultSelection(account);
  // ISO dates of the same shape compare correctly as strings.
  if (latest === null || !isMonday(candidate.weekStart) || candidate.weekStart > latest) return defaultSelection(first);
  return { accountId: account.id, weekStart: candidate.weekStart };
}
