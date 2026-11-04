// Notes are rendered exactly as the API sends them (no parsing, no re-wording).
export default function DataNotes({ notes }: { notes: string[] }) {
  if (notes.length === 0) return null;
  return (
    <ul className="data-notes" aria-label="Data notes">
      {notes.map((note) => (
        <li key={note}>
          <span aria-hidden="true">ⓘ </span>
          <span>{note}</span>
        </li>
      ))}
    </ul>
  );
}
