import React from "react";
import { CloseIcon } from "@/ui/icons";
import { NotificationProps } from "@/types/props/notification-props";
import { notificationVariantStyles } from "@/constants/notifications/notification-variants";

export const Notification: React.FC<NotificationProps> = ({
  id,
  variant,
  title,
  description,
  onClose,
  style,
  className = "",
}) => {
  const { borderColor, iconBg, icon } = notificationVariantStyles[variant];

  return (
    <div
      style={style}
      className={`flex items-start gap-3 w-full rounded-lg border-l-4 bg-white p-3.5 shadow-lg dark:bg-gray-800 ${borderColor} ${className}`}
    >
      <div className={`mt-0.5 flex shrink-0 items-center justify-center w-8 h-8 rounded-md ${iconBg}`}>
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <h4 className="wrap-break-word text-sm font-medium text-gray-800 dark:text-white/90">{title}</h4>
        {description && (
          <p className="mt-0.5 wrap-break-word text-xs text-gray-500 dark:text-white/70">{description}</p>
        )}
      </div>
      <button
        onClick={() => onClose(id)}
        className="shrink-0 text-gray-400 transition-colors hover:text-gray-600 dark:hover:text-white/70"
      >
        <CloseIcon />
      </button>
    </div>
  );
};
