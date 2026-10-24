import type { HomeTone } from "@/types/home/home-types";

export const homeToneClasses: Record<HomeTone, string> = {
  primary:
    "bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400",
  success:
    "bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-500",
  warning:
    "bg-warning-50 text-warning-600 dark:bg-warning-500/15 dark:text-orange-400",
  info:
    "bg-blue-light-50 text-blue-light-600 dark:bg-blue-light-500/15 dark:text-blue-light-400",
  light: "bg-gray-100 text-gray-700 dark:bg-white/5 dark:text-white/80",
};
