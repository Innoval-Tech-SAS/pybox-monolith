import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Textarea } from "@/ui/components/inputs/textarea";
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
        <Textarea
          id="cmp-description"
          rows={3}
          value={form.description}
          onChange={(e) => set("description")(e.target.value)}
          placeholder="Una breve descripción"
        />
      </div>
    </div>
  </Card>
);
