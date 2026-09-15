import React, { useState } from "react";
import { StepIndicator } from "@/ui/components/step-indicator";
import { VerticalStepIndicator } from "@/ui/components/vertical-step-indicator";
import { Spinner } from "@/ui/components/loader/spinner";
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
  // Bloquea el botón de envío justo después de pasar al último paso: el botón
  // "Continuar" del paso anterior queda en la misma posición que el botón de
  // envío, así que un doble clic (o un clic ligeramente rápido) en "Continuar"
  // puede caer también sobre "Crear campaña" y enviar el formulario sin que
  // el usuario lo note.
  const [submitGuard, setSubmitGuard] = useState(false);

  const goNext = () => {
    setStep((s) => {
      const next = s + 1;
      if (next === steps.length - 1) {
        setSubmitGuard(true);
        setTimeout(() => setSubmitGuard(false), 400);
      }
      return next;
    });
  };

  const goBack = () => {
    setStep((s) => s - 1);
    onBack?.();
  };

  // Evita el envío implícito del formulario al presionar Enter en un campo
  // (p. ej. los inputs de fecha/hora) cuando ya existe un botón submit en el DOM.
  const preventEnterSubmit = (e: React.KeyboardEvent<HTMLFormElement>) => {
    const tag = (e.target as HTMLElement).tagName;
    if (e.key === "Enter" && tag !== "TEXTAREA" && tag !== "BUTTON") {
      e.preventDefault();
    }
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
          disabled={loading || !canSubmit || submitGuard}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-50"
        >
          {loading && <Spinner size="xs" tone="white" />}
          {loading ? loadingLabel : submitLabel}
        </button>
      )}
    </div>
  );

  if (orientation === "vertical") {
    return (
      <form
        onSubmit={onSubmit}
        onKeyDown={preventEnterSubmit}
        className="flex min-h-0 flex-1 flex-col gap-6 lg:flex-row lg:gap-8"
      >
        <VerticalStepIndicator steps={steps} current={step} />
        <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-5">
          <div className="min-h-0 min-w-0 flex-1 overflow-y-auto custom-scrollbar">{children(step)}</div>
          {navButtons}
        </div>
      </form>
    );
  }

  return (
    <div className="flex h-full w-full flex-col gap-5">
      <StepIndicator current={step} total={steps.length} />

      <form onSubmit={onSubmit} onKeyDown={preventEnterSubmit} className="flex min-h-0 w-full flex-1 flex-col gap-5">
        <div className="min-h-0 w-full flex-1 overflow-y-auto custom-scrollbar">{children(step)}</div>
        {navButtons}
      </form>
    </div>
  );
};
