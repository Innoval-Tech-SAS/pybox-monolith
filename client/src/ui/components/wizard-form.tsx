import React, { useState } from "react";
import { StepIndicator } from "@/ui/components/step-indicator";
import { VerticalStepIndicator } from "@/ui/components/vertical-step-indicator";
import type { WizardFormProps } from "@/types/props/wizard-form-props";

export const WizardForm: React.FC<WizardFormProps> = ({
  steps,
  orientation = "horizontal",
  canAdvance,
  canSubmit,
  onSubmit,
  onBack,
  loading = false,
  submitLabel = "Finalizar",
  loadingLabel = "Guardando...",
  children,
}) => {
  const [step, setStep] = useState(0);

  const goNext = () => setStep((s) => s + 1);

  const goBack = () => {
    setStep((s) => s - 1);
    onBack?.();
  };

  const navButtons = (
    <div className={`flex gap-3 ${step > 0 ? "justify-between" : "justify-end"}`}>
      {step > 0 && (
        <button
          type="button"
          onClick={goBack}
          className="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Atrás
        </button>
      )}
      {step < steps.length - 1 ? (
        <button
          type="button"
          onClick={goNext}
          disabled={!canAdvance(step)}
          className="rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          Continuar
        </button>
      ) : (
        <button
          type="submit"
          disabled={loading || !canSubmit}
          className="rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          {loading ? loadingLabel : submitLabel}
        </button>
      )}
    </div>
  );

  if (orientation === "vertical") {
    return (
      <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col gap-6 lg:flex-row lg:gap-8">
        <VerticalStepIndicator steps={steps} current={step} />
        <div className="flex min-h-0 flex-1 flex-col gap-5">
          <div className="min-h-0 flex-1">{children(step)}</div>
          {navButtons}
        </div>
      </form>
    );
  }

  return (
    <div className="flex h-full flex-col gap-5">
      <StepIndicator current={step} total={steps.length} />

      <form onSubmit={onSubmit} className="flex min-h-0 flex-1 flex-col gap-5">
        <div className="min-h-0 flex-1">{children(step)}</div>
        {navButtons}
      </form>
    </div>
  );
};
