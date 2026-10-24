import type { SupportTicketPriority, SupportTicketStatus } from "@/types/support/support-types";

export const TICKET_FILTER_STATUSES: SupportTicketStatus[] = [
  "NUEVO",
  "ABIERTO",
  "EN_PROGRESO",
  "PENDIENTE_CLIENTE",
  "PENDIENTE_TERCERO",
  "RESUELTO",
  "CERRADO",
];

export const TICKET_FILTER_PRIORITIES: SupportTicketPriority[] = ["BAJA", "MEDIA", "ALTA", "URGENTE"];
