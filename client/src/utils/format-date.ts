type DateInput = string | number | Date | null | undefined;

const toValidDate = (value: DateInput): Date | null => {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
};

export const formatDate = (
  value: DateInput,
  options: Intl.DateTimeFormatOptions,
  fallback = "—",
  locale = "es-CO",
): string => {
  const date = toValidDate(value);
  if (!date) return fallback;
  return new Intl.DateTimeFormat(locale, options).format(date);
};

export const formatLongDate = (value: DateInput, fallback = "—"): string =>
  formatDate(value, { year: "numeric", month: "long", day: "numeric" }, fallback);

export const formatShortDate = (value: DateInput, fallback = "—"): string =>
  formatDate(value, { day: "2-digit", month: "short", year: "numeric" }, fallback);

export const formatDateTime = (value: DateInput, fallback = "—"): string =>
  formatDate(value, { dateStyle: "short", timeStyle: "short" }, fallback);

export const formatDateTimeLong = (value: DateInput, fallback = "—"): string =>
  formatDate(
    value,
    { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" },
    fallback,
  );
