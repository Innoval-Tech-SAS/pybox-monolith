import React from "react";
import { Link } from "react-router";
import { Home } from "lucide-react";
import { BreadcrumbProps, BreadcrumbItem } from "@/types/props/breadcrumb-props";

const ChevronRight: React.FC = () => (
  <svg
    className="stroke-current text-gray-400 dark:text-gray-600"
    width="17"
    height="16"
    viewBox="0 0 17 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M6.0765 12.667L10.2432 8.50033L6.0765 4.33366"
      strokeWidth="1.2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ItemContent: React.FC<{ item: BreadcrumbItem }> = ({ item }) => {
  const Icon = item.icon;
  return (
    <span className="inline-flex items-center gap-1.5">
      {Icon && <Icon size={15} />}
      {item.label}
    </span>
  );
};

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  pageTitle,
  pageIcon: PageIcon,
  items = [],
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 dark:text-white/90">
        {pageTitle}
      </h2>
      <nav>
        <ol className="flex items-center gap-1.5">
          <li className="flex items-center gap-1.5">
            <Link
              to="/home"
              aria-label="Home"
              className="inline-flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <Home size={16} />
            </Link>
            <ChevronRight />
          </li>
          {items.map((item, index) => (
            <li key={index} className="flex items-center gap-1.5">
              {item.path ? (
                <Link
                  to={item.path}
                  className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <ItemContent item={item} />
                </Link>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-sm text-gray-800 dark:text-white/90">
                  <ItemContent item={item} />
                </span>
              )}
              <ChevronRight />
            </li>
          ))}
          <li className="inline-flex items-center gap-1.5 text-sm text-gray-800 dark:text-white/90">
            {PageIcon && <PageIcon size={15} />}
            {pageTitle}
          </li>
        </ol>
      </nav>
    </div>
  );
};
