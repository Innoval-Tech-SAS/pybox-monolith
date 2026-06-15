import React from "react";
import {
  AlertHexaIcon,
  CheckCircleIcon,
  ErrorHexaIcon,
  InfoIcon,
} from "@/ui/icons";
import { NotificationVariant } from "@/types/props/notification-props";
import type { VariantStyle } from "./types/notification-variant-style";

export const notificationVariantStyles: Record<NotificationVariant, VariantStyle> = {
  success: {
    borderColor: "border-l-success-500",
    iconBg: "bg-success-50 text-success-500",
    icon: <CheckCircleIcon />,
  },
  info: {
    borderColor: "border-l-blue-light-500",
    iconBg: "bg-blue-light-50 text-blue-light-500",
    icon: <InfoIcon />,
  },
  warning: {
    borderColor: "border-l-warning-500",
    iconBg: "bg-warning-50 text-warning-500",
    icon: <AlertHexaIcon />,
  },
  error: {
    borderColor: "border-l-error-500",
    iconBg: "bg-error-50 text-error-500",
    icon: <ErrorHexaIcon className="size-5" />,
  },
};
