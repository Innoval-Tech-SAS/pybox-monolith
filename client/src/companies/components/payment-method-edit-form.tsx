import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { useEditPaymentMethodForm } from "@/companies/hooks/use-edit-payment-method-form";
import { usePaymentMethodTypes } from "@/companies/hooks/use-payment-method-types";
import { PaymentMethodEditGeneral } from "./payment-method-edit-general";
import { PaymentMethodEditBank } from "./payment-method-edit-bank";
import { Button } from "@/ui/components/button/button";
import type { PaymentMethodEditFormProps } from "@/companies/types/payment-method-edit-form-props";

export const PaymentMethodEditForm: React.FC<PaymentMethodEditFormProps> = ({
  item,
  orgId,
  onSuccess,
  onCancel,
}) => {
  const { types } = usePaymentMethodTypes();
  const { form, saving, field, setType, toggleActive, submit } = useEditPaymentMethodForm(
    item,
    item.id,
    orgId,
    onSuccess,
  );

  const typeOptions = types.map((t) => ({ value: t, label: PAYMENT_METHOD_TYPE_LABELS[t] ?? t }));

  return (
    <form onSubmit={submit}>
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <PaymentMethodEditGeneral
          form={form}
          typeOptions={typeOptions}
          field={field}
          setType={setType}
          toggleActive={toggleActive}
        />
        <PaymentMethodEditBank form={form} field={field} />
      </div>

      <div className="mt-5 flex items-center justify-end gap-3">
        <Button type="button" size="sm" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" size="sm" loading={saving} loadingText="Guardando...">
          Guardar cambios
        </Button>
      </div>
    </form>
  );
};
