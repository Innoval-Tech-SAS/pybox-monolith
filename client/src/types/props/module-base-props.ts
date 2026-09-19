import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import type { BreadcrumbItem } from "@/types/props/breadcrumb-props";

export interface ModuleBaseProps {
  pageTitle: string;
  pageIcon?: LucideIcon;
  breadcrumbItems?: BreadcrumbItem[];
  /** Force the "Volver" button on/off. Defaults to showing it when there are breadcrumb items. */
  showBack?: boolean;
  children: ReactNode;
}
