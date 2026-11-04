import type { Account } from "../api/types";

interface Props {
  accounts: Account[];
  accountId: number;
  onChange: (accountId: number) => void;
}

export default function AccountPicker({ accounts, accountId, onChange }: Props) {
  return (
    <div className="picker-row">
      <label htmlFor="account-select">Account</label>
      <select id="account-select" value={accountId} onChange={(e) => onChange(Number(e.target.value))}>
        {accounts.map((account) => (
          <option key={account.id} value={account.id}>
            {account.name}
          </option>
        ))}
      </select>
    </div>
  );
}
