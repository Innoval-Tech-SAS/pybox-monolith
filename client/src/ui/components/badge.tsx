import { colorStyles } from "@/types/props/badge-props";
import type { BadgeProps } from "@/types/props/badge-props";

export const Badge: React.FC<BadgeProps> = ({
  variant = "light",
  color = "primary",
  size = "md",
  startIcon,
  endIcon,
  children,
}) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 justify-center gap-1 rounded-full font-medium ${
      size === "sm" ? "text-theme-xs" : "text-sm"
    } ${colorStyles[variant][color]}`}
  >
    {startIcon && <span className="mr-1">{startIcon}</span>}
    {children}
    {endIcon && <span className="ml-1">{endIcon}</span>}
  </span>
);
