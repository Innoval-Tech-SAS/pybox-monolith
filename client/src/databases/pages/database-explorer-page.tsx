import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { Plus, Table2, Wrench } from "lucide-react";
import { PageMeta } from "@/ui/pages/page-meta";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Card, CardTitle } from "@/ui/components/card";
import { Select } from "@/ui/components/inputs/select";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";
import { useSchemas } from "@/databases/hooks/use-schemas";
import { useSchemaTables } from "@/databases/hooks/use-schema-tables";
import { useTableFields } from "@/databases/hooks/use-table-fields";

export const DatabaseExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const { schemas, loading: loadingSchemas } = useSchemas();
  const [schema, setSchema] = useState("public");
  const [table, setTable] = useState("");

  const { tables, loading: loadingTables } = useSchemaTables(schema);
  const { fields, loading: loadingFields } = useTableFields(schema, table);

  useEffect(() => {
    setTable("");
  }, [schema]);

  return (
    <>
      <PageMeta title="Bases de datos" description="Explorar y administrar esquemas, tablas y columnas" />
      <ModuleBase pageTitle="Bases de datos" breadcrumbItems={[]} showBack>
        <div className="flex flex-col gap-5">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div className="w-full max-w-xs">
              <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-400">Esquema</label>
              <Select
                options={schemas.map((s) => ({ value: s, label: s }))}
                value={schema}
                onChange={setSchema}
                disabled={loadingSchemas}
              />
            </div>
            <button
              onClick={() => navigate("/databases/tables/new")}
              className="inline-flex items-center gap-2 rounded-lg bg-brand-500 px-4 py-2.5 text-sm font-medium text-white shadow-theme-xs hover:bg-brand-600"
            >
              <Plus size={16} />
              Nueva tabla
            </button>
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <Card>
              <CardTitle>Tablas de {schema}</CardTitle>
              {loadingTables ? (
                <Loader />
              ) : tables.length === 0 ? (
                <EmptyState icon={Table2} title="No hay tablas en este esquema" />
              ) : (
                <div className="flex max-h-[60vh] flex-col gap-1 overflow-y-auto custom-scrollbar">
                  {tables.map((t) => (
                    <button
                      key={t}
                      onClick={() => setTable(t)}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition ${
                        t === table
                          ? "bg-brand-50 font-medium text-brand-600 dark:bg-brand-500/10 dark:text-brand-400"
                          : "text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-white/5"
                      }`}
                    >
                      <Table2 size={15} />
                      {t}
                    </button>
                  ))}
                </div>
              )}
            </Card>

            <Card>
              <div className="mb-4 flex items-center justify-between">
                <CardTitle>{table ? `Columnas de ${table}` : "Columnas"}</CardTitle>
                {table && (
                  <button
                    onClick={() => navigate(`/databases/tables/alter?schema=${schema}&table=${table}`)}
                    className="flex items-center gap-1.5 text-sm font-medium text-brand-500 hover:text-brand-600"
                  >
                    <Wrench size={14} />
                    Alterar tabla
                  </button>
                )}
              </div>

              {!table ? (
                <p className="text-sm text-gray-400 dark:text-gray-500">Selecciona una tabla para ver sus columnas.</p>
              ) : loadingFields ? (
                <Loader />
              ) : (
                <div className="max-h-[60vh] divide-y divide-gray-100 overflow-y-auto custom-scrollbar dark:divide-gray-800">
                  {fields.map((f) => (
                    <div key={f.name} className="flex items-center justify-between py-2 text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">{f.name}</span>
                      <span className="text-gray-400 dark:text-gray-500">{f.type}</span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      </ModuleBase>
    </>
  );
};
