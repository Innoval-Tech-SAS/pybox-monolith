import type { AppNotification } from "@/types/notifications/notification";

export interface NotificationRowProps {
  notification: AppNotification;
  isSelected: boolean;
  onClick: () => void;
}
