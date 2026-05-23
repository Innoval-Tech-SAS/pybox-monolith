import type { NotificationVariant } from "../props/notification-props";

export interface Toast {
  id: string;
  variant: NotificationVariant;
  title: string;
  description?: string;
}

export interface ToastContextValue {
  toasts: Toast[];
  dismiss: (id: string) => void;
  success: (title: string, description?: string) => void;
  error: (title: string, description?: string) => void;
  info: (title: string, description?: string) => void;
  warning: (title: string, description?: string) => void;
}
