export interface DropdownItemProps {
  tag?: "button" | "link";
  to?: string;
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
}
