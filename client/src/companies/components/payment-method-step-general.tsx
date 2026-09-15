import { Card } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
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
        <textarea
          id="instructions"
          rows={3}
          value={form.instructions}
          onChange={field("instructions")}
          placeholder="Instrucciones de pago"
          className="w-full resize-none rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        />
      </div>
    </div>
  </Card>
);
