export { formatCop, formatUsd } from "@/utils/format-currency";

export const formatPeriod = (year: number, month: number): string => {
  const date = new Date(year, month - 1, 1);
  return date.toLocaleDateString("es-CO", { year: "numeric", month: "long" });
};
