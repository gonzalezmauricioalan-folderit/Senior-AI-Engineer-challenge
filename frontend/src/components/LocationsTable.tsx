import type { LocationMetric } from "../api/types";
import { formatNumber, formatPct } from "../format";
import StatusBadge from "./StatusBadge";

/*
 * Ranked locations (PLAN.md 3.7, wireframe in PLAN_first_iteration.md).
 *
 *   locations = []  -> header "Locations (0)" + "No locations with activity yet." (no table)
 *   locations = [..] -> header + <table>, one row per item, in the order the API sent
 *
 * The API already ranks the rows (lower_than_usual by biggest drop first, then the rest by name,
 * not_enough_history last), so this component never sorts, filters or recomputes a status.
 * Nulls (usual / pct for a location without history) render as "—".
 */
export default function LocationsTable({ locations }: { locations: LocationMetric[] }) {
  return (
    <section className="locations" aria-labelledby="locations-heading">
      <div className="locations-header">
        <h2 id="locations-heading">Locations ({locations.length})</h2>
        <span className="muted">needs attention first</span>
      </div>
      {locations.length === 0 ? (
        <p className="muted">No locations with activity yet.</p>
      ) : (
        <table>
          <caption className="visually-hidden">Locations, needs attention first</caption>
          <thead>
            <tr>
              <th scope="col">Location</th>
              <th scope="col" className="num">This week</th>
              <th scope="col" className="num">Usual</th>
              <th scope="col" className="num">vs usual</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {locations.map((row) => (
              <tr key={row.location}>
                <th scope="row">
                  {row.location}
                  {row.low_volume && (
                    <span className="tag" title="Low weekly volume: results may be unreliable.">
                      Low volume
                    </span>
                  )}
                </th>
                <td className="num">{row.total}</td>
                <td className="num">{row.usual === null ? "—" : `~${formatNumber(row.usual)}`}</td>
                <td className="num">{formatPct(row.pct_vs_usual)}</td>
                <td>
                  <StatusBadge status={row.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
