import type { IvrCallStatus } from "../types/ivr-monitor-types";

export const CALL_STATUS_LABELS: Record<IvrCallStatus, string> = {
  QUEUED: "En cola",
  RINGING: "Timbrando",
  HUMAN_DETECTED: "Contestó una persona",
  MACHINE_DETECTED: "Contestadora",
  IN_IVR: "En el menú",
  TRANSFERRING: "Transfiriendo",
  COMPLETED: "Completada",
  NO_ANSWER: "Sin respuesta",
  FAILED: "Fallida",
  CANCELLED: "Cancelada",
};

/** Clases Tailwind del badge de estado (claro + oscuro). */
export const CALL_STATUS_CLASSES: Record<IvrCallStatus, string> = {
  QUEUED: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  RINGING: "bg-blue-50 text-blue-600 dark:bg-blue-500/15 dark:text-blue-400",
  HUMAN_DETECTED: "bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400",
  MACHINE_DETECTED: "bg-orange-50 text-orange-600 dark:bg-orange-500/15 dark:text-orange-400",
  IN_IVR: "bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-400",
  TRANSFERRING: "bg-purple-50 text-purple-600 dark:bg-purple-500/15 dark:text-purple-400",
  COMPLETED: "bg-success-50 text-success-700 dark:bg-success-500/15 dark:text-success-400",
  NO_ANSWER: "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-warning-400",
  FAILED: "bg-error-50 text-error-600 dark:bg-error-500/15 dark:text-error-400",
  CANCELLED: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

/** Estados que siguen "vivos": la fila muestra un indicador pulsante. */
export const LIVE_CALL_STATUSES: IvrCallStatus[] = [
  "QUEUED",
  "RINGING",
  "HUMAN_DETECTED",
  "MACHINE_DETECTED",
  "IN_IVR",
  "TRANSFERRING",
];

export const AMD_LABELS: Record<string, string> = {
  HUMAN: "Persona",
  MACHINE: "Máquina",
  NOTSURE: "Dudoso",
  HANGUP: "Colgó",
};

export const DIAL_STATUS_LABELS: Record<string, string> = {
  ANSWER: "Contestó",
  NOANSWER: "No contestó",
  BUSY: "Ocupado",
  CONGESTION: "Congestión",
  CHANUNAVAIL: "Canal no disponible",
};
