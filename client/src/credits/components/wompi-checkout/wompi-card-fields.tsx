import { Input } from "@/ui/components/inputs/input";
import type { WompiCardFieldsProps } from "@/credits/types/wompi-card-fields-props";

export const WompiCardFields: React.FC<WompiCardFieldsProps> = ({ value, onChange }) => (
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
    <div className="sm:col-span-2">
      <Input
        label="Número de tarjeta"
        id="wompi-card-number"
        maxLength={19}
        value={value.number}
        onChange={(e) => onChange({ ...value, number: e.target.value.replace(/\D/g, "") })}
        placeholder="4242 4242 4242 4242"
      />
    </div>
    <Input
      label="Mes de expiración"
      id="wompi-card-exp-month"
      maxLength={2}
      value={value.expMonth}
      onChange={(e) => onChange({ ...value, expMonth: e.target.value.replace(/\D/g, "") })}
      placeholder="MM"
    />
    <Input
      label="Año de expiración"
      id="wompi-card-exp-year"
      maxLength={2}
      value={value.expYear}
      onChange={(e) => onChange({ ...value, expYear: e.target.value.replace(/\D/g, "") })}
      placeholder="AA"
    />
    <Input
      label="CVC"
      id="wompi-card-cvc"
      maxLength={4}
      value={value.cvc}
      onChange={(e) => onChange({ ...value, cvc: e.target.value.replace(/\D/g, "") })}
      placeholder="123"
    />
    <Input
      label="Cuotas"
      id="wompi-card-installments"
      type="number"
      min="1"
      max="36"
      value={value.installments}
      onChange={(e) => onChange({ ...value, installments: Number(e.target.value) || 1 })}
    />
    <div className="sm:col-span-2">
      <Input
        label="Nombre del titular"
        id="wompi-card-holder"
        value={value.cardHolder}
        onChange={(e) => onChange({ ...value, cardHolder: e.target.value })}
        placeholder="Como aparece en la tarjeta"
      />
    </div>
  </div>
);
