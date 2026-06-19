import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import type { StepDetailsProps } from "@/campaigns/types/step-details-props";

export const StepDetails: React.FC<StepDetailsProps> = ({ form, channels, set }) => (
  <Card className="flex h-full flex-col">
    <CardTitle>Detalles de la campaña</CardTitle>
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      <div className="sm:col-span-2">
        <Input
          label="Nombre *"
          id="cmp-name"
          value={form.name}
          onChange={(e) => set("name")(e.target.value)}
          placeholder="Ej: Recuperación preventiva"
        />
      </div>

      <div className="sm:col-span-2">
        <Input
          label="Descripción"
          id="cmp-description"
          value={form.description}
          onChange={(e) => set("description")(e.target.value)}
          placeholder="Una breve descripción"
        />
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Canal *
        </label>
        <Select
          options={channels.map((c) => ({ value: c.id, label: c.label }))}
          value={form.channelId}
          onChange={(v) => set("channelId")(v)}
        />
      </div>

      <div>
        <Input
          label="Zona horaria"
          id="cmp-timezone"
          value={form.timezone}
          onChange={(e) => set("timezone")(e.target.value)}
          placeholder="UTC"
        />
      </div>
    </div>
  </Card>
);
