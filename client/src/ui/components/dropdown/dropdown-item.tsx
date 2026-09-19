import { Link } from "react-router";
import { DropdownItemProps } from "@/types/props/dropdown-item-props";

export const DropdownItem: React.FC<DropdownItemProps> = ({
  to,
  onClick,
  onItemClick,
  children,
  tag = "button",
  className = "",
  type = "button",
  baseClassName = "block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-gray-300",
}) => {
  const combinedClasses = `${baseClassName} ${className}`.trim();

  const handleClick = (event: React.MouseEvent) => {
    if (tag === "button") {
      event.preventDefault();
    }
    if (onClick) onClick();
    if (onItemClick) onItemClick();
  };

  if (tag === "a" && to) {
    return (
      <Link to={to} className={combinedClasses} onClick={handleClick}>
        {children}
      </Link>
    );
  }

  return (
    <button type={type} onClick={handleClick} className={combinedClasses}>
      {children}
    </button>
  );
};
