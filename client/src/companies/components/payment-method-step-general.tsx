import { Card } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { Textarea } from "@/ui/components/inputs/textarea";
import type { PaymentMethodStepGeneralProps } from "@/companies/types/payment-method-form-props";

export const PaymentMethodStepGeneral: React.FC<PaymentMethodStepGeneralProps> = ({
  form,
  typeOptions,
  field,
  setType,
}) => (
  <Card>
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
    </div>
  </Card>
);
