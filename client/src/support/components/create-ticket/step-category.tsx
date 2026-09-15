import { CategoryCard } from "./category-card";
import type { StepCategoryProps } from "@/support/types/step-category-props";

export const StepCategory: React.FC<StepCategoryProps> = ({
  categories,
  loading,
  selectedCategory,
  onSelectCategory,
  canGoNext,
  onNext,
  onCancel,
}) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-xl font-bold text-gray-800 dark:text-white/90">¿En qué podemos ayudarte?</h2>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Selecciona la categoría que mejor describe tu situación.
      </p>
    </div>

    {loading ? (
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-xl bg-gray-100 dark:bg-white/5" />
        ))}
      </div>
    ) : (
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        {categories.map((cat) => (
          <CategoryCard
            key={cat.topic}
            category={cat}
            selected={selectedCategory?.topic === cat.topic}
            onSelect={() => onSelectCategory(cat)}
          />
        ))}
      </div>
    )}

    <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
      <button
        type="button"
        onClick={onCancel}
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 transition hover:bg-gray-50 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700 dark:hover:bg-white/3"
      >
        Cancelar
      </button>
      <button
        type="button"
        disabled={!canGoNext}
        onClick={onNext}
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-6 py-3 text-sm font-medium text-white shadow-theme-xs transition hover:bg-brand-600 disabled:opacity-50"
      >
        Continuar
      </button>
    </div>
  </div>
);
