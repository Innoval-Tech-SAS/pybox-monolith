export const formatMonthlyPeriod = (period: string): string => {
  const [year, month] = period.split("-");
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleDateString("es-CO", { month: "short", year: "2-digit" });
};
