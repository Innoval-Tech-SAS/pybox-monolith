import type { NotifType } from "@/types/notifications/notification";

export interface NotifIconProps {
  type: NotifType;
  size?: "sm" | "md" | "lg";
}
