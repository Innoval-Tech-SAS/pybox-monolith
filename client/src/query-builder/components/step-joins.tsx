import { Plus, Trash2 } from "lucide-react";
import { Select } from "@/ui/components/inputs/select";
import { useEntityFields } from "@/query-builder/hooks/use-entity-fields";
import { JOIN_TYPES } from "@/query-builder/constants/query-builder-constants";
import type { JoinHow } from "@/query-builder/types/query-builder-types";
import type { StepJoinsProps, JoinRowProps } from "@/query-builder/types/step-joins-props";

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

  const { fields: leftFields } = useEntityFields(leftTable?.name ?? "");
  const { fields: rightFields } = useEntityFields(rightTable?.name ?? "");

  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-white/3">
      <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
        <div className="w-32 shrink-0">
          <Select
            value={join.how}
            onChange={(v) => onChange({ how: v as JoinHow })}
            options={JOIN_TYPES.map((jt) => ({ value: jt.value, label: jt.label }))}
          />
        </div>
        <span className="shrink-0 text-xs text-gray-400">entre</span>

        <div className="min-w-0 flex-1">
          <Select
            value={join.left}
            onChange={(v) => onChange({ left: v, leftOn: "" })}
            options={tables.map((t) => ({ value: t.alias, label: t.alias }))}
          />
        </div>

        <span className="shrink-0 text-xs text-gray-400">y</span>

        <div className="min-w-0 flex-1">
          <Select
            value={join.right}
            onChange={(v) => onChange({ right: v, rightOn: "" })}
            options={tables.map((t) => ({ value: t.alias, label: t.alias }))}
          />
        </div>

        <span className="shrink-0 text-xs text-gray-400">on</span>

        <div className="min-w-0 flex-1">
          <Select
            value={join.leftOn}
            onChange={(v) => onChange({ leftOn: v })}
            placeholder={`Campo de ${join.left}…`}
            options={leftFields.map((f) => ({ value: f.name, label: f.name }))}
          />
        </div>

        <span className="shrink-0 text-xs text-gray-400">=</span>

        <div className="min-w-0 flex-1">
          <Select
            value={join.rightOn}
            onChange={(v) => onChange({ rightOn: v })}
            placeholder={`Campo de ${join.right}…`}
            options={rightFields.map((f) => ({ value: f.name, label: f.name }))}
          />
        </div>

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
