export interface DropdownItemProps {
  tag?: "a" | "button";
  to?: string;
  onClick?: () => void;
  onItemClick?: () => void;
  baseClassName?: string;
  className?: string;
  type?: "button" | "reset" | "submit";
  children: React.ReactNode;
}
