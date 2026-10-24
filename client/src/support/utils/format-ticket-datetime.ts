import { formatDateTimeLong } from "@/utils/format-date";

export const formatTicketDateTime = (iso: string): string => formatDateTimeLong(iso);
