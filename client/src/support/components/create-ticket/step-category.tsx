import { CategoryCard } from "./category-card";
import { Button } from "@/ui/components/button/button";
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
      <Button type="button" variant="outline" onClick={onCancel}>
        Cancelar
      </Button>
      <Button type="button" disabled={!canGoNext} onClick={onNext}>
        Continuar
      </Button>
    </div>
  </div>
);
