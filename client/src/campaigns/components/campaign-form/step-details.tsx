import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import type { StepDetailsProps } from "@/campaigns/types/step-details-props";

export const StepDetails: React.FC<StepDetailsProps> = ({ form, set }) => (
  <Card className="flex h-full flex-col">
    <CardTitle>Detalles de la campaña</CardTitle>
    <div className="grid grid-cols-1 gap-5">
      <div>
        <Input
          label="Nombre *"
          id="cmp-name"
          value={form.name}
          onChange={(e) => set("name")(e.target.value)}
          placeholder="Ej: Recuperación preventiva"
        />
      </div>

      <div>
        <label htmlFor="cmp-description" className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Descripción
        </label>
        <textarea
          id="cmp-description"
          rows={3}
          value={form.description}
          onChange={(e) => set("description")(e.target.value)}
          placeholder="Una breve descripción"
          className="w-full rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        />
      </div>
    </div>
  </Card>
);
