import type { ReactNode } from "react";

export interface StatCardProps {
  icon: ReactNode;
  label: string;
  value: string | number;
  /** Resalta la card como la métrica protagonista (borde y numeral en brand-500). */
  accent?: boolean;
}
