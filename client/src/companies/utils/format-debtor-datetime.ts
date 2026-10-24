import { formatDateTime } from "@/utils/format-date";

export const formatDebtorDateTime = (value: string | null): string =>
  formatDateTime(value, "Sin fecha");
