export const formatCop = (value: string | number): string => {
  const num = typeof value === "string" ? Number(value) : value;
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(Number.isFinite(num) ? num : 0);
};

export const formatUsd = (value: string | number): string => {
  const num = typeof value === "string" ? Number(value) : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 4,
  }).format(Number.isFinite(num) ? num : 0);
};

export const formatPeriod = (year: number, month: number): string => {
  const date = new Date(year, month - 1, 1);
  return date.toLocaleDateString("es-CO", { year: "numeric", month: "long" });
};
