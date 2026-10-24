import type { BadgeColor } from "@/types/props/badge-props";

export const CONTACT_STATUS_COLOR: Record<string, BadgeColor> = {
  SENT: "info",
  ANSWERED: "success",
  DELIVERED: "success",
  OPENED: "success",
  CLICKED: "success",
  FORM_OPENED: "success",
  FORM_SUBMITTED: "success",
  PENDING: "warning",
  NO_ANSWER: "warning",
  SOFT_BOUNCED: "warning",
  FAILED: "error",
  REJECTED: "error",
  EXPIRED: "error",
  UNDELIVERED: "error",
  HARD_BOUNCED: "error",
  COMPLAINT: "error",
  FORM_REJECTED: "error",
  UNSUBSCRIBED: "light",
  UNSUBSCRIBED_LANDING: "light",
};
