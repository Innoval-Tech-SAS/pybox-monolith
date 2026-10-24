import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Textarea } from "@/ui/components/inputs/textarea";
import { Switch } from "@/ui/components/switch";
import type { PaymentMethodEditGeneralProps } from "@/companies/types/payment-method-edit-form-props";

export const PaymentMethodEditGeneral: React.FC<PaymentMethodEditGeneralProps> = ({
  form,
  typeOptions,
  field,
  setType,
  toggleActive,
}) => (
  <Card>
    <CardTitle>Información general</CardTitle>
    <div className="grid grid-cols-1 gap-5">
      <Input
        label="Nombre *"
        id="name"
        value={form.name}
        onChange={field("name")}
        placeholder="Nombre del método"
      />
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Tipo <span className="text-error-500">*</span>
        </label>
        <Select
          options={typeOptions}
          value={form.type}
          placeholder="Seleccionar tipo"
          onChange={setType}
        />
      </div>
      <Input
        label="Descripción"
        id="description"
        value={form.description}
        onChange={field("description")}
        placeholder="Descripción opcional"
      />
      <div>
        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
          Instrucciones
        </label>
        <Textarea
          id="instructions"
          rows={3}
          value={form.instructions}
          onChange={field("instructions")}
          placeholder="Instrucciones de pago"
          className="resize-none"
        />
      </div>
      <div>
        <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-400">Estado</p>
        <Switch
          checked={form.isActive}
          onChange={() => toggleActive()}
          label={form.isActive ? "Activo" : "Inactivo"}
        />
      </div>
    </div>
  </Card>
);
