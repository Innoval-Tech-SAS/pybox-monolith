import type { NavItem } from "@/types/navigation/nav-item";

export interface AsideMenuProps {
  navItems?: NavItem[];
  othersItems?: NavItem[];
  othersLabel?: string;
  supportItems?: NavItem[];
  supportLabel?: string;
  logoUrl?: string | null;
}
