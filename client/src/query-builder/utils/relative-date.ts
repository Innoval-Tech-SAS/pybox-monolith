export type RelativeMode = "fixed" | "now" | "offset" | "this_week" | "this_month";

const OFFSET_RE = /^@now([+-]\d+)d$/;

export const isDateLikeType = (type: string): boolean => /date|timestamp/i.test(type);

export const buildOffsetToken = (days: number): string => `@now${days >= 0 ? "+" : ""}${days}d`;

export const RELATIVE_VALUE_OPTIONS: { value: RelativeMode; label: string }[] = [
  { value: "fixed", label: "Valor fijo" },
  { value: "now", label: "Ahora" },
  { value: "offset", label: "Ahora ± N días" },
  { value: "this_week", label: "Esta semana" },
  { value: "this_month", label: "Este mes" },
];

export const detectRelativeMode = (
  op: string,
  value: string | string[] | null,
): { mode: RelativeMode; days: number } => {
  if (op === "between" && Array.isArray(value)) {
    if (value[0] === "@week_start" && value[1] === "@week_end") return { mode: "this_week", days: 0 };
    if (value[0] === "@month_start" && value[1] === "@month_end") return { mode: "this_month", days: 0 };
  }
  if (typeof value === "string") {
    if (value === "@now") return { mode: "now", days: 0 };
    const match = OFFSET_RE.exec(value);
    if (match) return { mode: "offset", days: parseInt(match[1], 10) };
  }
  return { mode: "fixed", days: 0 };
};

export const relativeValueLabel = (op: string, value: string | string[] | null): string | null => {
  const { mode, days } = detectRelativeMode(op, value);
  switch (mode) {
    case "now":
      return "ahora";
    case "offset":
      return days === 0 ? "ahora" : `ahora ${days > 0 ? "+" : ""}${days} día${Math.abs(days) === 1 ? "" : "s"}`;
    case "this_week":
      return "esta semana";
    case "this_month":
      return "este mes";
    default:
      return null;
  }
};
