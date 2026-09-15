import { Check, ChevronLeft, ChevronRight } from "lucide-react";
import { StepIndicator } from "@/ui/components/step-indicator";
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
          <button
            type="button"
            onClick={prevStep}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            <ChevronLeft size={16} />
            Anterior
          </button>
        ) : (
          <button
            type="button"
            onClick={onCancel}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-theme-xs hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
          >
            <ChevronLeft size={16} />
            Cancelar
          </button>
        )}

        {isLastStep ? (
          <button
            type="submit"
            disabled={saving || !form.name.trim() || !form.type}
            className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
          >
            <Check size={16} />
            {saving ? "Creando..." : "Crear método"}
          </button>
        ) : (
          <button
            type="submit"
            disabled={!canNext}
            className="inline-flex items-center gap-1.5 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600 disabled:opacity-50"
          >
            Siguiente
            <ChevronRight size={16} />
          </button>
        )}
      </div>
    </form>
  );
};
