import { useCallback, useEffect, useState } from "react";

export interface RequestState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
  reload: () => void;
}

interface Settled<T> {
  // Which request this result belongs to. `loading` is derived by comparing it with the current
  // request, so no setState is needed synchronously inside the effect.
  source: unknown;
  nonce: number;
  data: T | null;
  error: Error | null;
}

/**
 * Runs `fetcher` whenever its identity (or a manual reload) changes and aborts the previous
 * request, so a slow stale response can never overwrite a newer one.
 * `fetcher` must be memoised by the caller; `null` means "nothing to request".
 */
export function useRequest<T>(fetcher: ((signal: AbortSignal) => Promise<T>) | null): RequestState<T> {
  const [nonce, setNonce] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);

  useEffect(() => {
    if (!fetcher) return;
    const controller = new AbortController();
    fetcher(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) setSettled({ source: fetcher, nonce, data, error: null });
      },
      (error: unknown) => {
        if (controller.signal.aborted) return;
        setSettled({
          source: fetcher,
          nonce,
          data: null,
          error: error instanceof Error ? error : new Error(String(error)),
        });
      },
    );
    return () => controller.abort();
  }, [fetcher, nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  if (!fetcher) return { data: null, error: null, loading: false, reload };
  const current = settled !== null && settled.source === fetcher && settled.nonce === nonce;
  return {
    data: current ? settled.data : null,
    error: current ? settled.error : null,
    loading: !current,
    reload,
  };
}
