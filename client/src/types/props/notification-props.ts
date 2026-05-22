export type NotificationVariant = "success" | "info" | "warning" | "error";

export interface NotificationProps {
  id: string;
  variant: NotificationVariant;
  title: string;
  description?: string;
  onClose: (id: string) => void;
}
