type IconBtnVariant = "default" | "warning" | "primary" | "success" | "error";

const ICON_BTN_VARIANTS: Record<IconBtnVariant, string> = {
  default: "text-gray-400 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-500 dark:hover:bg-white/8 dark:hover:text-gray-300",
  warning: "text-gray-400 hover:bg-warning-50 hover:text-warning-600 dark:text-gray-500 dark:hover:bg-warning-500/10 dark:hover:text-warning-400",
  primary: "text-gray-400 hover:bg-brand-50 hover:text-brand-600 dark:text-gray-500 dark:hover:bg-brand-500/10 dark:hover:text-brand-400",
  success: "text-gray-400 hover:bg-success-50 hover:text-success-600 dark:text-gray-500 dark:hover:bg-success-500/10 dark:hover:text-success-400",
  error:   "text-gray-400 hover:bg-error-50 hover:text-error-600 dark:text-gray-500 dark:hover:bg-error-500/10 dark:hover:text-error-400",
};

export const IconBtn = ({ onClick, title, variant = "default", children }: { onClick: () => void; title: string; variant?: IconBtnVariant; children: React.ReactNode }) => (
  <button
    type="button"
    title={title}
    aria-label={title}
    onClick={onClick}
    className={`flex min-h-10 min-w-10 items-center justify-center rounded-lg p-2 transition-all ${ICON_BTN_VARIANTS[variant]}`}
  >
    {children}
  </button>
);
