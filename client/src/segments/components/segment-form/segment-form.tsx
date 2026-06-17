import { ChevronLeft } from "lucide-react";
import { StepIndicator } from "@/ui/components/step-indicator";
import { Loader } from "@/ui/components/loader/loader";
import { StepBasicInfo } from "./step-basic-info";
import { StepTablesFilters } from "./step-tables-filters";
import { StepJoins } from "./step-joins";
import { StepAggregation } from "./step-aggregation";
import { StepSummary } from "./step-summary";
import { useSegmentForm } from "@/segments/hooks/use-segment-form";
import { SEGMENT_STEPS } from "@/segments/constants/segment.constants";
import type { SegmentFormProps } from "@/segments/types/segment-form-props";

export const SegmentForm: React.FC<SegmentFormProps> = ({
  orgId,
  onSuccess,
  onCancel,
  existing,
}) => {
  const {
    step,
    state,
    update,
    submitting,
    nextStep,
    prevStep,
    addTable,
    removeTable,
    updateTable,
    addJoin,
    removeJoin,
    updateJoin,
    submit,
    allTableAliases,
  } = useSegmentForm(orgId, onSuccess, existing);

  const isLastStep = step === SEGMENT_STEPS.length - 1;

  const canNext = () => {
    if (step === 0) return !!state.name.trim() && !!state.mainTable;
    if (step === 3 && state.aggregateMode) {
      return state.aggregations.length > 0 && state.aggregations.every((a) => !!a.column && !!a.alias);
    }
    return true;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={step === 0 ? onCancel : prevStep}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-gray-500 transition hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          <ChevronLeft size={16} />
          {step === 0 ? "Cancelar" : "Atrás"}
        </button>
        <h2 className="text-base font-semibold text-gray-800 dark:text-white">
          {existing ? "Editar segmento" : "Nuevo segmento"} — {SEGMENT_STEPS[step]}
        </h2>
      </div>

      <StepIndicator current={step} total={SEGMENT_STEPS.length} />

      {/* Step content */}
      <div>
        {step === 0 && <StepBasicInfo state={state} update={update} />}
        {step === 1 && (
          <StepTablesFilters
            state={state}
            update={update}
            addTable={addTable}
            removeTable={removeTable}
            updateTable={updateTable}
          />
        )}
        {step === 2 && (
          <StepJoins
            state={state}
            addJoin={addJoin}
            removeJoin={removeJoin}
            updateJoin={updateJoin}
            allTableAliases={allTableAliases}
          />
        )}
        {step === 3 && <StepAggregation state={state} update={update} />}
        {step === 4 && <StepSummary state={state} />}
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 border-t border-gray-100 pt-4 dark:border-gray-800">
        {isLastStep ? (
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="flex items-center gap-2 rounded-xl bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:opacity-50"
          >
            {submitting ? <Loader /> : (existing ? "Guardar cambios" : "Crear segmento")}
          </button>
        ) : (
          <button
            type="button"
            onClick={nextStep}
            disabled={!canNext()}
            className="rounded-xl bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:opacity-40"
          >
            Siguiente
          </button>
        )}
      </div>
    </div>
  );
};
