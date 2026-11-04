// Aliases over the generated schema so components never import schema.d.ts directly.
// Regenerate the schema with `npm run gen:api`; never edit it by hand.
import type { components } from "./schema";

type Schemas = components["schemas"];

export type Account = Schemas["AccountSummary"];
export type WeeklyInsight = Schemas["WeeklyInsight"];
export type Metric = Schemas["Metric"];
export type LocationMetric = Schemas["LocationMetric"];
export type Day = Schemas["Day"];
export type Status = Schemas["Status"];
