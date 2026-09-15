export const formatCurrency = (
  value: number | string | null | undefined,
  currency = "COP",
  options: Partial<Intl.NumberFormatOptions> = {},
  locale = "es-CO",
): string => {
  const num = typeof value === "string" ? Number(value) : value;
  const safeNum = Number.isFinite(num as number) ? (num as number) : 0;

  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
      ...options,
    }).format(safeNum);
  } catch {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(safeNum);
  }
};

export const formatCop = (value: number | string): string => formatCurrency(value, "COP");

export const formatUsd = (value: number | string): string =>
  formatCurrency(value, "USD", { maximumFractionDigits: 4 }, "en-US");
