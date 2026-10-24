import { Input } from "@/ui/components/inputs/input";
import { Label } from "@/ui/components/inputs/label";
import { Select } from "@/ui/components/inputs/select";
import { PSE_LEGAL_ID_TYPE_OPTIONS } from "@/credits/constants/pse-legal-id-types";
import type { PayuPayerFieldsProps } from "@/credits/types/payu-payer-fields-props";

/**
 * Exigidos por PayU para NEQUI y BANCOLOMBIA_TRANSFER (buyer/payer completos, igual
 * que PSE -- ver `PayUGateway.create_transaction`) -- Wompi/Bold ignoran estos campos
 * para estos dos métodos.
 */
export const PayuPayerFields: React.FC<PayuPayerFieldsProps> = ({ value, onChange, idPrefix }) => (
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
    <Input
      label="Nombre completo"
      id={`${idPrefix}-full-name`}
      value={value.fullName}
      onChange={(e) => onChange({ ...value, fullName: e.target.value })}
    />
    <div>
      <Label htmlFor={`${idPrefix}-legal-id-type`}>Tipo de documento</Label>
      <Select
        id={`${idPrefix}-legal-id-type`}
        options={PSE_LEGAL_ID_TYPE_OPTIONS}
        value={value.userLegalIdType}
        onChange={(v) => onChange({ ...value, userLegalIdType: v })}
      />
    </div>
    <Input
      label="Número de documento"
      id={`${idPrefix}-legal-id`}
      value={value.userLegalId}
      onChange={(e) => onChange({ ...value, userLegalId: e.target.value.replace(/\D/g, "") })}
    />
    <Input
      label="Dirección"
      id={`${idPrefix}-address`}
      value={value.address}
      onChange={(e) => onChange({ ...value, address: e.target.value })}
    />
    <Input
      label="Ciudad"
      id={`${idPrefix}-city`}
      value={value.city}
      onChange={(e) => onChange({ ...value, city: e.target.value })}
    />
  </div>
);
