import type { LucideIcon } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: LucideIcon;
}

export interface BreadcrumbProps {
  pageTitle: string;
  pageIcon?: LucideIcon;
  items?: BreadcrumbItem[];
}
