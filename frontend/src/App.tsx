import { useEffect, useState } from "react";
import AccountPicker from "./components/AccountPicker";
import DailyChart from "./components/DailyChart";
import DataNotes from "./components/DataNotes";
import LocationsTable from "./components/LocationsTable";
import StateMessage from "./components/StateMessage";
import VerdictCard from "./components/VerdictCard";
import WeekPicker from "./components/WeekPicker";
import { useAccounts } from "./hooks/useAccounts";
import { useWeeklyInsight } from "./hooks/useWeeklyInsight";
import { defaultSelection, loadSelection, resolveSelection, saveSelection, type Selection } from "./storage";

export default function App() {
  const accounts = useAccounts();
  // What the user (or storage) asked for. It is validated against the accounts on every render
  // instead of being copied into state in an effect, so an invalid value can never be displayed.
  const [requested, setRequested] = useState<Selection | null>(loadSelection);

  const accountList = accounts.data;
  const selection = accountList ? resolveSelection(accountList, requested) : null;
  const account = selection && accountList ? accountList.find((a) => a.id === selection.accountId) : undefined;

  const insight = useWeeklyInsight(selection?.accountId ?? null, selection?.weekStart ?? null);

  // Saved on every change, and this also overwrites an invalid stored value with the defaults.
  const accountId = selection?.accountId;
  const weekStart = selection?.weekStart;
  useEffect(() => {
    if (accountId !== undefined && weekStart) saveSelection({ accountId, weekStart });
  }, [accountId, weekStart]);

  return (
    <main className="app">
      <h1>Relay · Weekly activity</h1>
      {accounts.loading && <StateMessage message="Loading…" />}
      {accounts.error && <StateMessage message="Couldn't load data." onRetry={accounts.reload} />}
      {accountList && accountList.length === 0 && <StateMessage message="No accounts found." />}
      {accountList && selection && account && (
        <>
          <div className="pickers">
            <AccountPicker
              accounts={accountList}
              accountId={selection.accountId}
              onChange={(id) => {
                // Changing account resets the week to that account's latest complete week.
                const next = accountList.find((a) => a.id === id);
                if (next) setRequested(defaultSelection(next));
              }}
            />
            {selection.weekStart && account.latest_complete_week && (
              <WeekPicker
                weekStart={selection.weekStart}
                latestWeek={account.latest_complete_week}
                timezone={account.timezone}
                onChange={(week) => setRequested({ accountId: account.id, weekStart: week })}
              />
            )}
          </div>
          {selection.weekStart === null && <StateMessage message="No complete week yet for this account." />}
          {insight.loading && <StateMessage message="Loading…" />}
          {insight.error && <StateMessage message="Couldn't load data." onRetry={insight.reload} />}
          {insight.data && (
            <>
              <VerdictCard summary={insight.data.summary} baseline={insight.data.baseline} />
              <DailyChart days={insight.data.days} />
              <LocationsTable locations={insight.data.locations} />
              <DataNotes notes={insight.data.data_notes} />
            </>
          )}
        </>
      )}
    </main>
  );
}
