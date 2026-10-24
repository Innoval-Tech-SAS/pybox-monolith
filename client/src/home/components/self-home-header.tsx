import { Mail } from "lucide-react";
import type { SelfHomeHeaderProps } from "@/types/props/self-home-props";

/** Saludo del titular y acceso al buzón judicial con su contador de no leídas. */
export const SelfHomeHeader: React.FC<SelfHomeHeaderProps> = ({
  firstName,
  unreadCount,
  onOpenInbox,
}) => (
  <header className="flex flex-wrap items-start justify-between gap-4">
    <div>
      <h1 className="text-title-sm font-semibold text-gray-800 dark:text-white/90">
        {firstName ? `Hola, ${firstName}` : "Hola"}
      </h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Este es el resumen de tus obligaciones a la fecha.
      </p>
    </div>

    <button
      type="button"
      onClick={onOpenInbox}
      className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs transition hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-200 dark:hover:bg-gray-800"
    >
      <Mail size={17} className="text-gray-500 dark:text-gray-400" />
      Buzón judicial
      {unreadCount > 0 && (
        <span className="flex size-5 items-center justify-center rounded-full bg-error-500 text-[11px] font-semibold text-white">
          {unreadCount}
        </span>
      )}
    </button>
  </header>
);
