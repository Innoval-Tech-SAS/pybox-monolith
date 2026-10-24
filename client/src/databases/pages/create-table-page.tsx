import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { WizardForm } from "@/ui/components/wizard-form";
import { Card, CardTitle } from "@/ui/components/card";
import { Input } from "@/ui/components/inputs/input";
import { Select } from "@/ui/components/inputs/select";
import { ColumnListEditor } from "@/databases/components/column-list-editor";
import { CREATE_TABLE_WIZARD_STEPS } from "@/databases/constants/table-wizard-options";
import { useCreateTable } from "@/databases/hooks/use-create-table";

export const CreateTablePage: React.FC = () => {
  const {
    schemas,
    loadingSchemas,
    schema,
    setSchema,
    tableName,
    setTableName,
    columns,
    setColumns,
    saving,
    locationValid,
    columnsValid,
    canAdvance,
    handleSubmit,
  } = useCreateTable();

  return (
    <>
      <PageMeta title="Nueva tabla" description="Crear una nueva tabla en la base de datos" />
      <ModuleBase pageTitle="Nueva tabla" breadcrumbItems={[{ label: "Bases de datos", path: "/databases" }]}>
        <WizardForm
          steps={CREATE_TABLE_WIZARD_STEPS}
          canAdvance={canAdvance}
          canSubmit={locationValid && columnsValid}
          onSubmit={handleSubmit}
          loading={saving}
          submitLabel="Crear tabla"
          loadingLabel="Creando…"
        >
          {(step) => (
            <>
              {step === 0 && (
                <Card className="flex h-full flex-col">
                  <CardTitle>Ubicación de la tabla</CardTitle>
                  <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                      <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">
                        Esquema
                      </label>
                      <Select
                        options={schemas.map((s) => ({ value: s, label: s }))}
                        value={schema}
                        onChange={setSchema}
                        disabled={loadingSchemas}
                      />
                    </div>
                    <Input
                      label="Nombre de la tabla *"
                      value={tableName}
                      onChange={(e) => setTableName(e.target.value)}
                      placeholder="Ej: contactos_adicionales"
                    />
                  </div>
                </Card>
              )}

              {step === 1 && (
                <Card className="flex h-full flex-col">
                  <CardTitle>Columnas</CardTitle>
                  <ColumnListEditor columns={columns} onChange={setColumns} />
                </Card>
              )}

              {step === 2 && (
                <Card className="flex h-full flex-col">
                  <CardTitle>Resumen</CardTitle>
                  <div className="space-y-4 text-sm">
                    <p>
                      Se creará la tabla <span className="font-medium text-gray-800 dark:text-white/90">{schema}.{tableName}</span> con {columns.length} columna(s):
                    </p>
                    <div className="divide-y divide-gray-100 rounded-lg border border-gray-200 dark:divide-gray-800 dark:border-gray-800">
                      {columns.map((c, i) => (
                        <div key={i} className="flex items-center justify-between px-4 py-2.5">
                          <span className="font-medium text-gray-700 dark:text-gray-300">
                            {c.name}
                            {c.primaryKey && <span className="ml-1.5 text-xs text-brand-500">PK</span>}
                            {c.unique && <span className="ml-1.5 text-xs text-gray-400">UNIQUE</span>}
                          </span>
                          <span className="text-gray-400 dark:text-gray-500">
                            {c.dataType}
                            {c.nullable ? "" : " · NOT NULL"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              )}
            </>
          )}
        </WizardForm>
      </ModuleBase>
    </>
  );
};
