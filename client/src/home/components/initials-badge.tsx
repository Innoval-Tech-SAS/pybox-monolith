import type { InitialsBadgeProps } from "@/types/props/initials-badge-props";
import { getInitials } from "../utils/initials-utils";

/** Insignia de iniciales (organización o portafolio): mismo lenguaje visual que el avatar del navbar (bg-brand-500). */
export const InitialsBadge: React.FC<InitialsBadgeProps> = ({ name }) => (
  <div className="flex items-center gap-3">
    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-500 text-sm font-semibold text-white">
      {getInitials(name)}
    </span>
    <h2 className="text-base font-semibold text-gray-800 dark:text-white/90">{name}</h2>
  </div>
);
