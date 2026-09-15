import { Check, ChevronLeft, ChevronRight } from "lucide-react";
import { StepIndicator } from "@/ui/components/step-indicator";
import { Button } from "@/ui/components/button/button";
import { PAYMENT_METHOD_TYPE_LABELS } from "@/constants/payment-methods/payment-method-labels";
import { usePaymentMethodForm, PAYMENT_METHOD_STEPS } from "@/companies/hooks/use-payment-method-form";
import { usePaymentMethodTypes } from "@/companies/hooks/use-payment-method-types";
import { PaymentMethodStepGeneral } from "./payment-method-step-general";
import { PaymentMethodStepBank } from "./payment-method-step-bank";
import { PaymentMethodStepSummary } from "./payment-method-step-summary";
import type { PaymentMethodFormProps } from "@/companies/types/payment-method-form-props";

export const PaymentMethodForm: React.FC<PaymentMethodFormProps> = ({ orgId, onSuccess, onCancel }) => {
  const { types } = usePaymentMethodTypes();
  const { form, step, saving, isLastStep, canNext, field, setType, prevStep, submit } =
    usePaymentMethodForm(orgId, onSuccess);

  const typeOptions = types.map((t) => ({ value: t, label: PAYMENT_METHOD_TYPE_LABELS[t] ?? t }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submit();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <StepIndicator current={step} total={PAYMENT_METHOD_STEPS.length} />
        <h2 className="text-base font-semibold text-gray-800 dark:text-white">
          {PAYMENT_METHOD_STEPS[step]}
        </h2>
      </div>

      {step === 0 && (
        <PaymentMethodStepGeneral form={form} typeOptions={typeOptions} field={field} setType={setType} />
      )}
      {step === 1 && <PaymentMethodStepBank form={form} field={field} />}
      {step === 2 && (
        <PaymentMethodStepSummary form={form} typeLabel={PAYMENT_METHOD_TYPE_LABELS[form.type] ?? form.type} />
      )}

      <div className="flex items-center justify-between gap-3 border-t border-gray-100 pt-4 dark:border-gray-800">
        {step > 0 ? (
          <Button type="button" size="sm" variant="outline" startIcon={<ChevronLeft size={16} />} onClick={prevStep}>
            Anterior
          </Button>
        ) : (
          <Button type="button" size="sm" variant="outline" startIcon={<ChevronLeft size={16} />} onClick={onCancel}>
            Cancelar
          </Button>
        )}

        {isLastStep ? (
          <Button
            type="submit"
            size="sm"
            disabled={!form.name.trim() || !form.type}
            loading={saving}
            loadingText="Creando..."
            startIcon={<Check size={16} />}
          >
            Crear método
          </Button>
        ) : (
          <Button type="submit" size="sm" disabled={!canNext} endIcon={<ChevronRight size={16} />}>
            Siguiente
          </Button>
        )}
      </div>
    </form>
  );
};
