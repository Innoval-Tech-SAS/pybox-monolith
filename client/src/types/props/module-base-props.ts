import type { ReactNode } from "react";
import type { BreadcrumbItem } from "@/types/props/breadcrumb-props";

export interface ModuleBaseProps {
  pageTitle: string;
  sectionTitle?: string;
  breadcrumbItems?: BreadcrumbItem[];
  children: ReactNode;
}
