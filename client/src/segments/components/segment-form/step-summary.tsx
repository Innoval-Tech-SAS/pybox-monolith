import { ALL_TABLES, JOIN_TYPES } from "@/segments/constants/segment.constants";
import type { StepSummaryProps, SectionProps, RowProps } from "@/segments/types/step-summary-props";

const tableLabel = (name: string) =>
  ALL_TABLES.find((t) => t.name === name)?.label ?? name;

const joinLabel = (how: string) =>
  JOIN_TYPES.find((j) => j.value === how)?.label ?? how;

export const StepSummary: React.FC<StepSummaryProps> = ({ state }) => {
  const allTables = [
    { name: state.mainTable, alias: state.mainTable, columns: state.mainTableColumns, filters: state.mainTableFilters, isMain: true },
    ...state.additionalTables.map((t) => ({ ...t, isMain: false })),
  ];

  return (
    <div className="space-y-5">
      {/* Basic info */}
      <Section title="Información básica">
        <Row label="Nombre" value={state.name} />
        {state.description && <Row label="Descripción" value={state.description} />}
        <Row label="Tabla principal" value={tableLabel(state.mainTable)} />
      </Section>

      {/* Tables */}
      <Section title="Tablas">
        {allTables.map((t) => (
          <div key={t.alias} className="mb-3">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
              {tableLabel(t.name)} {t.isMain && <span className="text-xs text-brand-500">(principal)</span>}
            </p>
            {t.columns.length > 0 ? (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Columnas: {t.columns.join(", ")}
              </p>
            ) : (
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5 italic">Todas las columnas</p>
            )}
            {t.filters.length > 0 && (
              <ul className="mt-1 space-y-0.5">
                {t.filters.map((f, i) => (
                  <li key={i} className="text-xs text-gray-500 dark:text-gray-400">
                    {f.column} {f.op} {f.value == null ? "" : Array.isArray(f.value) ? `[${f.value.join(", ")}]` : String(f.value)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </Section>

      {/* Joins */}
      {state.joins.length > 0 && (
        <Section title="Uniones">
          {state.joins.map((j, i) => (
            <p key={i} className="text-sm text-gray-700 dark:text-gray-300">
              {j.left}.{j.leftOn} <span className="text-xs text-gray-500">{joinLabel(j.how)}</span> {j.right}.{j.rightOn}
            </p>
          ))}
        </Section>
      )}
    </div>
  );
};

const Section: React.FC<SectionProps> = ({ title, children }) => (
  <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-white/3">
    <h3 className="mb-3 text-sm font-semibold text-gray-800 dark:text-white">{title}</h3>
    <div className="space-y-2">{children}</div>
  </div>
);

const Row: React.FC<RowProps> = ({ label, value }) => (
  <div className="flex justify-between py-1">
    <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
    <span className="text-sm font-medium text-gray-800 dark:text-white">{value}</span>
  </div>
);
