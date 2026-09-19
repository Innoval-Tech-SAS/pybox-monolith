import { AlertTriangle } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { WizardForm } from "@/ui/components/wizard-form";
import { Card, CardTitle } from "@/ui/components/card";
import { ALTER_TABLE_WIZARD_STEPS } from "@/databases/constants/table-wizard-options";
import { ALTER_TABLE_ACTION_SUMMARY } from "@/databases/constants/alter-table-action-summary";
import { StepAlterTarget } from "@/databases/components/table-form/step-alter-target";
import { StepAlterChange } from "@/databases/components/table-form/step-alter-change";
import { useAlterTable } from "@/databases/hooks/use-alter-table";

export const AlterTablePage: React.FC = () => {
  const {
    schemas,
    tables,
    fields,
    form,
    set,
    saving,
    targetValid,
    changeValid,
    canAdvance,
    handleSubmit,
  } = useAlterTable();

  return (
    <>
      <PageMeta title="Alterar tabla" description="Agregar, eliminar, modificar o renombrar columnas" />
      <ModuleBase pageTitle="Alterar tabla" breadcrumbItems={[{ label: "Bases de datos", path: "/databases" }]}>
        <WizardForm
          steps={ALTER_TABLE_WIZARD_STEPS}
          canAdvance={canAdvance}
          canSubmit={targetValid && changeValid}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel="Aplicar cambio"
          loadingLabel="Aplicando…"
        >
          {(step) => (
            <>
              {step === 0 && <StepAlterTarget form={form} set={set} schemas={schemas} tables={tables} />}
              {step === 1 && <StepAlterChange form={form} set={set} fields={fields} />}
              {step === 2 && (
                <Card className="flex h-full flex-col">
                  <CardTitle>Resumen</CardTitle>
                  {form.action === "DROP_COLUMN" ? (
                    <div className="flex items-start gap-2 rounded-lg bg-error-50 px-3 py-2.5 text-sm text-error-700 dark:bg-error-500/15 dark:text-error-400">
                      <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                      <p>
                        {ALTER_TABLE_ACTION_SUMMARY[form.action](form)} Esta acción es irreversible: los datos de esa
                        columna se pierden de forma permanente.
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-700 dark:text-gray-300">{ALTER_TABLE_ACTION_SUMMARY[form.action](form)}</p>
                  )}
                </Card>
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
