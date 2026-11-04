import { useCallback } from "react";
import { getWeeklyInsight } from "../api/client";
import type { WeeklyInsight } from "../api/types";
import { useRequest, type RequestState } from "./useRequest";

/** `weekStart = null` disables the request (an account with no complete week has no insight). */
export function useWeeklyInsight(accountId: number | null, weekStart: string | null): RequestState<WeeklyInsight> {
  const fetcher = useCallback(
    (signal: AbortSignal) => getWeeklyInsight(accountId as number, weekStart as string, signal),
    [accountId, weekStart],
  );
  return useRequest(accountId === null || weekStart === null ? null : fetcher);
}
