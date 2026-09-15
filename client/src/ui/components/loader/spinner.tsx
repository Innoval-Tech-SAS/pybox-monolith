import { SpinnerProps } from "@/types/props/spinner-props";

const sizeClasses: Record<NonNullable<SpinnerProps["size"]>, string> = {
  xs: "w-4 h-4",
  sm: "w-5 h-5",
  md: "w-10 h-10",
};

const toneClasses: Record<NonNullable<SpinnerProps["tone"]>, string> = {
  muted:
    "border-gray-200 border-t-gray-500 dark:border-white/20 dark:border-t-brand-500",
  white: "border-white border-t-transparent",
  current: "border-current border-t-transparent",
  brand: "border-brand-500/30 border-t-brand-500",
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  tone = "muted",
  className = "",
}) => (
  <div
    role="status"
    aria-label="Cargando"
    className={`${sizeClasses[size]} rounded-full border-2 animate-spin ${toneClasses[tone]} ${className}`}
  />
);
