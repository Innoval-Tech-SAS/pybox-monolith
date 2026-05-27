export interface DropdownItemProps {
  tag?: "button" | "a" | "link";
  to?: string;
  onClick?: () => void;
  onItemClick?: () => void;
  className?: string;
  baseClassName?: string;
  type?: "button" | "submit" | "reset";
  children: React.ReactNode;
}
