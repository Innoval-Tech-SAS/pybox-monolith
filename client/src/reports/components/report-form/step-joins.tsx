import { Plus, Trash2 } from "lucide-react";
import { useReportFields } from "@/reports/hooks/use-report-fields";
import { JOIN_TYPES } from "@/reports/constants/report.constants";
import type { JoinHow } from "@/reports/types/report.types";
import type { StepJoinsProps, JoinRowProps } from "@/reports/types/step-joins-props";

export const StepJoins: React.FC<StepJoinsProps> = ({
  state,
  addJoin,
  removeJoin,
  updateJoin,
}) => {
  const tables = [
    { alias: state.mainTable, name: state.mainTable },
    ...state.additionalTables.map((t) => ({ alias: t.alias, name: t.name })),
  ];

  const handleAdd = () => {
    if (tables.length < 2) return;
    addJoin({
      left: tables[0].alias,
      right: tables[1]?.alias ?? tables[0].alias,
      leftOn: "",
      rightOn: "",
      how: "inner",
    });
  };

  if (tables.length < 2) {
    return (
      <div className="flex flex-col items-center gap-3 py-10 text-center">
        <span className="text-3xl">🔗</span>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Agrega al menos una tabla adicional en el paso anterior para configurar uniones.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Define cómo se relacionan las tablas entre sí.
      </p>

      {state.joins.length === 0 ? (
        <p className="text-xs text-gray-400 dark:text-gray-500">Sin uniones configuradas.</p>
      ) : (
        <div className="space-y-3">
          {state.joins.map((join, i) => (
            <JoinRow
              key={i}
              join={join}
              tables={tables}
              onChange={(patch) => updateJoin(i, patch)}
              onRemove={() => removeJoin(i)}
            />
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={handleAdd}
        className="flex items-center gap-1.5 rounded-lg border border-dashed border-brand-300 px-3 py-2 text-sm text-brand-500 transition hover:border-brand-400 hover:bg-brand-50 dark:border-brand-700 dark:hover:bg-brand-500/10"
      >
        <Plus size={15} /> Agregar unión
      </button>
    </div>
  );
};

const JoinRow: React.FC<JoinRowProps> = ({ join, tables, onChange, onRemove }) => {
  const leftTable = tables.find((t) => t.alias === join.left);
  const rightTable = tables.find((t) => t.alias === join.right);

  const { fields: leftFields } = useReportFields(leftTable?.name ?? "");
  const { fields: rightFields } = useReportFields(rightTable?.name ?? "");

  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-white/3">
      <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
        <select
          value={join.how}
          onChange={(e) => onChange({ how: e.target.value as JoinHow })}
          className="min-w-0 shrink-0 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs font-medium text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        >
          {JOIN_TYPES.map((jt) => (
            <option key={jt.value} value={jt.value}>{jt.label}</option>
          ))}
        </select>
        <span className="shrink-0 text-xs text-gray-400">entre</span>

        <select
          value={join.left}
          onChange={(e) => onChange({ left: e.target.value, leftOn: "" })}
          className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        >
          {tables.map((t) => (
            <option key={t.alias} value={t.alias}>{t.alias}</option>
          ))}
        </select>

        <span className="shrink-0 text-xs text-gray-400">y</span>

        <select
          value={join.right}
          onChange={(e) => onChange({ right: e.target.value, rightOn: "" })}
          className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        >
          {tables.map((t) => (
            <option key={t.alias} value={t.alias}>{t.alias}</option>
          ))}
        </select>

        <span className="shrink-0 text-xs text-gray-400">on</span>

        <select
          value={join.leftOn}
          onChange={(e) => onChange({ leftOn: e.target.value })}
          className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        >
          <option value="">Campo de {join.left}…</option>
          {leftFields.map((f) => (
            <option key={f.name} value={f.name}>{f.name}</option>
          ))}
        </select>

        <span className="shrink-0 text-xs text-gray-400">=</span>

        <select
          value={join.rightOn}
          onChange={(e) => onChange({ rightOn: e.target.value })}
          className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        >
          <option value="">Campo de {join.right}…</option>
          {rightFields.map((f) => (
            <option key={f.name} value={f.name}>{f.name}</option>
          ))}
        </select>

        <button
          type="button"
          onClick={onRemove}
          className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
};
