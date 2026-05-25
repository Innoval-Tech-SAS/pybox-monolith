export type NotifType = "success" | "info" | "warning" | "error";

export interface AppNotification {
  id: number;
  title: string;
  body: string;
  category: string;
  notifType: NotifType;
  isRead: boolean;
  createdAt: string;
  link?: string;
  details?: Record<string, unknown>;
}
