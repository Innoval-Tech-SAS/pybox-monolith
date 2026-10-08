import { HelpCircle } from "lucide-react";
import { TICKET_CATEGORY_ICON_MAP } from "@/support/constants/ticket-category-icons";
import type { CategoryCardProps } from "@/support/types/category-card-props";

export const CategoryCard: React.FC<CategoryCardProps> = ({ category, selected, onSelect }) => {
  const Icon = TICKET_CATEGORY_ICON_MAP[category.icon] ?? HelpCircle;
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`flex items-start gap-3 rounded-xl border p-4 text-left transition-all ${
        selected
          ? "border-brand-500 bg-brand-50 dark:border-brand-400 dark:bg-brand-500/10"
          : "border-gray-200 bg-white hover:border-brand-300 hover:bg-gray-50 dark:border-gray-700 dark:bg-white/3 dark:hover:border-brand-600 dark:hover:bg-white/5"
      }`}
    >
      <div
        className={`mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg ${
          selected
            ? "bg-brand-100 text-brand-600 dark:bg-brand-500/20 dark:text-brand-400"
            : "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-400"
        }`}
      >
        <Icon size={17} />
      </div>
      <div>
        <p
          className={`text-sm font-semibold ${
            selected ? "text-brand-700 dark:text-brand-300" : "text-gray-800 dark:text-white/90"
          }`}
        >
          {category.label}
        </p>
        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{category.description}</p>
      </div>
    </button>
  );
};
