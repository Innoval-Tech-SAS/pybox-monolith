import {
  ArrowRightLeft,
  ArrowUpCircle,
  CheckCircle,
  Flag,
  Plus,
  RefreshCw,
  UserCheck,
  XCircle,
} from "lucide-react";
import type { TicketEventType } from "@/types/support/support-types";

export const TICKET_EVENT_LABELS: Record<TicketEventType, string> = {
  CREADO: "Ticket creado",
  CAMBIO_ESTADO: "Estado cambiado",
  CAMBIO_PRIORIDAD: "Prioridad cambiada",
  ASIGNADO: "Asignado",
  REASIGNADO: "Reasignado",
  ESCALADO: "Escalado",
  RESUELTO: "Resuelto",
  CERRADO: "Cerrado",
  REABIERTO: "Reabierto",
};

export const TICKET_EVENT_ICON: Record<TicketEventType, React.ReactNode> = {
  CREADO: <Plus size={12} />,
  CAMBIO_ESTADO: <ArrowRightLeft size={12} />,
  CAMBIO_PRIORIDAD: <Flag size={12} />,
  ASIGNADO: <UserCheck size={12} />,
  REASIGNADO: <UserCheck size={12} />,
  ESCALADO: <ArrowUpCircle size={12} />,
  RESUELTO: <CheckCircle size={12} />,
  CERRADO: <XCircle size={12} />,
  REABIERTO: <RefreshCw size={12} />,
};

export const TICKET_EVENT_COLOR: Record<TicketEventType, string> = {
  CREADO: "bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400",
  CAMBIO_ESTADO: "bg-gray-100 text-gray-600 dark:bg-white/10 dark:text-gray-400",
  CAMBIO_PRIORIDAD: "bg-orange-100 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400",
  ASIGNADO: "bg-success-50 text-success-600 dark:bg-success-500/20 dark:text-success-400",
  REASIGNADO: "bg-warning-50 text-warning-600 dark:bg-warning-500/20 dark:text-warning-400",
  ESCALADO: "bg-error-50 text-error-600 dark:bg-error-500/20 dark:text-error-400",
  RESUELTO: "bg-success-50 text-success-600 dark:bg-success-500/20 dark:text-success-400",
  CERRADO: "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-500",
  REABIERTO: "bg-brand-50 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400",
};
