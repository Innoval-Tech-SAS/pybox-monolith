export interface NavItem {
  name: string;
  icon: React.ReactNode;
  path?: string;
  new?: boolean;
  subItems?: { name: string; path: string }[];
}
