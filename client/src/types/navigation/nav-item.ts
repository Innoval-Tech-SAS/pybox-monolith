import type { ReactNode } from "react";

export interface NavSubItem {
  name: string;
  path: string;
}

export interface NavItem {
  name: string;
  icon: ReactNode;
  path?: string;
  new?: boolean;
  subItems?: NavSubItem[];
}
