import type { NotifIconProps } from "@/notifications/types/notif-icon-props";
import { NOTIF_ICON_CONFIG as ICON_CONFIG } from "../constants/notif-icon-config";

const SIZE_CLASSES = {
  sm: "h-8 w-8",
  md: "h-10 w-10",
  lg: "h-14 w-14",
};

export const NotifIcon: React.FC<NotifIconProps> = ({ type, size = "md" }) => {
  const { bg, icon } = ICON_CONFIG[type] ?? ICON_CONFIG.info;
  return (
    <span className={`shrink-0 flex items-center justify-center rounded-full ${SIZE_CLASSES[size]} ${bg}`}>
      {icon}
    </span>
  );
};
