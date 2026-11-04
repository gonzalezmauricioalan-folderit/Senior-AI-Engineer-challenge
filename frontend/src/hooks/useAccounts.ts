import { getAccounts } from "../api/client";
import type { Account } from "../api/types";
import { useRequest, type RequestState } from "./useRequest";

export function useAccounts(): RequestState<Account[]> {
  return useRequest(getAccounts);
}
