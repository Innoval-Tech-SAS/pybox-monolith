import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/input";
import { Select } from "@/ui/components/inputs/select";
import type { PaymentMethodEditGeneralProps } from "@/companies/types/payment-method-edit-form-props";

const SWITCH_BASE =
  "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none";

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
        <textarea
          id="instructions"
          rows={3}
          value={form.instructions}
          onChange={field("instructions")}
          placeholder="Instrucciones de pago"
          className="w-full resize-none rounded-lg border border-gray-300 bg-transparent px-4 py-2.5 text-sm text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-300 focus:outline-hidden focus:ring-3 focus:ring-brand-500/20 dark:border-gray-700 dark:bg-gray-900 dark:text-white/90 dark:placeholder:text-white/30"
        />
      </div>
      <div>
        <p className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-400">Estado</p>
        <button
          type="button"
          role="switch"
          aria-checked={form.isActive}
          onClick={toggleActive}
          className={`${SWITCH_BASE} ${form.isActive ? "bg-brand-500" : "bg-gray-200 dark:bg-gray-700"}`}
        >
          <span
            className={`inline-block size-5 rounded-full bg-white shadow transition-transform ${
              form.isActive ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
        <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
          {form.isActive ? "Activo" : "Inactivo"}
        </span>
      </div>
    </div>
  </Card>
);
