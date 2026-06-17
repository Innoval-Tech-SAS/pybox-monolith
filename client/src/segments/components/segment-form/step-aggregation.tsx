import { Plus, Trash2 } from "lucide-react";
import { Switch } from "@/ui/components/switch";
import { useSegmentFields } from "@/segments/hooks/use-segment-fields";
import { AGG_FUNCTIONS, HAVING_OPS, HAVING_OPS_WITH_MULTIPLE_VALUES } from "@/segments/constants/segment.constants";
import type {
  AggFunction,
  HavingOp,
  SegmentAggregation,
  SegmentGroupBy,
  SegmentHaving,
  SegmentOrderBy,
  SortDirection,
} from "@/segments/types/segment.types";
import type {
  StepAggregationProps,
  SegmentTableRef,
  GroupByRowProps,
  AggregationRowProps,
  HavingRowProps,
  OrderByRowProps,
} from "@/segments/types/step-aggregation-props";

const selectClass =
  "min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300";

export const StepAggregation: React.FC<StepAggregationProps> = ({ state, update }) => {
  const tables: SegmentTableRef[] = [
    { alias: state.mainTable, name: state.mainTable },
    ...state.additionalTables.map((t) => ({ alias: t.alias, name: t.name })),
  ];

  const metricOptions = state.aggregations.map((a) => a.alias).filter(Boolean);
  const fieldOptions = [...state.groupBy.map((g) => g.alias), ...metricOptions].filter(Boolean);

  const addGroupBy = () => {
    const firstTable = tables[0];
    const group: SegmentGroupBy = { table: firstTable?.alias ?? "", column: "", alias: "" };
    update({ groupBy: [...state.groupBy, group] });
  };

  const updateGroupBy = (i: number, patch: Partial<SegmentGroupBy>) =>
    update({ groupBy: state.groupBy.map((g, idx) => (idx === i ? { ...g, ...patch } : g)) });

  const removeGroupBy = (i: number) =>
    update({ groupBy: state.groupBy.filter((_, idx) => idx !== i) });

  const addAggregation = () => {
    const firstTable = tables[0];
    const aggregation: SegmentAggregation = {
      function: "count",
      table: firstTable?.alias ?? "",
      column: "*",
      alias: `count_${state.aggregations.length + 1}`,
    };
    update({ aggregations: [...state.aggregations, aggregation] });
  };

  const updateAggregation = (i: number, patch: Partial<SegmentAggregation>) =>
    update({ aggregations: state.aggregations.map((a, idx) => (idx === i ? { ...a, ...patch } : a)) });

  const removeAggregation = (i: number) => {
    const removedAlias = state.aggregations[i]?.alias;
    update({
      aggregations: state.aggregations.filter((_, idx) => idx !== i),
      having: state.having.filter((h) => h.metric !== removedAlias),
      orderBy: state.orderBy.filter((o) => o.field !== removedAlias),
    });
  };

  const addHaving = () => {
    const firstMetric = metricOptions[0] ?? "";
    const having: SegmentHaving = { metric: firstMetric, op: ">", value: "" };
    update({ having: [...state.having, having] });
  };

  const updateHaving = (i: number, patch: Partial<SegmentHaving>) =>
    update({ having: state.having.map((h, idx) => (idx === i ? { ...h, ...patch } : h)) });

  const removeHaving = (i: number) =>
    update({ having: state.having.filter((_, idx) => idx !== i) });

  const addOrderBy = () => {
    const order: SegmentOrderBy = { field: fieldOptions[0] ?? "", direction: "desc" };
    update({ orderBy: [...state.orderBy, order] });
  };

  const updateOrderBy = (i: number, patch: Partial<SegmentOrderBy>) =>
    update({ orderBy: state.orderBy.map((o, idx) => (idx === i ? { ...o, ...patch } : o)) });

  const removeOrderBy = (i: number) =>
    update({ orderBy: state.orderBy.filter((_, idx) => idx !== i) });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-white/3">
        <div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-200">Agrupar y agregar resultados</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Activa esto para usar COUNT, SUM, AVG, MIN o MAX (por ejemplo: deudores con más de un crédito vencido).
          </p>
        </div>
        <Switch
          checked={state.aggregateMode}
          onChange={(checked) => update({ aggregateMode: checked })}
        />
      </div>

      {!state.aggregateMode ? (
        <p className="text-xs text-gray-400 dark:text-gray-500">
          El segmento devolverá el detalle fila por fila, sin agrupar.
        </p>
      ) : (
        <>
          {/* Group by */}
          <Section
            title="Agrupar por"
            description="Columnas usadas para agrupar las filas (ej. id del deudor)."
            onAdd={addGroupBy}
            addLabel="Agregar columna"
          >
            {state.groupBy.length === 0 ? (
              <p className="text-xs text-gray-400 dark:text-gray-500">Sin columnas de agrupación.</p>
            ) : (
              <div className="space-y-2">
                {state.groupBy.map((g, i) => (
                  <GroupByRow
                    key={i}
                    group={g}
                    tables={tables}
                    onChange={(patch) => updateGroupBy(i, patch)}
                    onRemove={() => removeGroupBy(i)}
                  />
                ))}
              </div>
            )}
          </Section>

          {/* Aggregations */}
          <Section
            title="Agregaciones"
            description="Métricas calculadas por grupo (COUNT, SUM, AVG, MIN, MAX)."
            onAdd={addAggregation}
            addLabel="Agregar métrica"
          >
            {state.aggregations.length === 0 ? (
              <p className="text-xs text-gray-400 dark:text-gray-500">Sin agregaciones. Se requiere al menos una.</p>
            ) : (
              <div className="space-y-2">
                {state.aggregations.map((a, i) => (
                  <AggregationRow
                    key={i}
                    aggregation={a}
                    tables={tables}
                    onChange={(patch) => updateAggregation(i, patch)}
                    onRemove={() => removeAggregation(i)}
                  />
                ))}
              </div>
            )}
          </Section>

          {/* Having */}
          <Section
            title="Filtrar grupos (HAVING)"
            description="Condiciones sobre las métricas, ej. count_creditos > 1."
            onAdd={addHaving}
            addLabel="Agregar condición"
            disabled={metricOptions.length === 0}
          >
            {state.having.length === 0 ? (
              <p className="text-xs text-gray-400 dark:text-gray-500">Sin condiciones sobre los grupos.</p>
            ) : (
              <div className="space-y-2">
                {state.having.map((h, i) => (
                  <HavingRow
                    key={i}
                    having={h}
                    metricOptions={metricOptions}
                    onChange={(patch) => updateHaving(i, patch)}
                    onRemove={() => removeHaving(i)}
                  />
                ))}
              </div>
            )}
          </Section>

          {/* Order by */}
          <Section
            title="Ordenar por"
            description="Orden de los resultados agrupados."
            onAdd={addOrderBy}
            addLabel="Agregar orden"
            disabled={fieldOptions.length === 0}
          >
            {state.orderBy.length === 0 ? (
              <p className="text-xs text-gray-400 dark:text-gray-500">Sin orden definido.</p>
            ) : (
              <div className="space-y-2">
                {state.orderBy.map((o, i) => (
                  <OrderByRow
                    key={i}
                    order={o}
                    fieldOptions={fieldOptions}
                    onChange={(patch) => updateOrderBy(i, patch)}
                    onRemove={() => removeOrderBy(i)}
                  />
                ))}
              </div>
            )}
          </Section>
        </>
      )}
    </div>
  );
};

const Section: React.FC<{
  title: string;
  description: string;
  onAdd: () => void;
  addLabel: string;
  disabled?: boolean;
  children: React.ReactNode;
}> = ({ title, description, onAdd, addLabel, disabled, children }) => (
  <div className="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
    <div className="mb-2 flex items-center justify-between">
      <div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{title}</p>
        <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500">{description}</p>
      </div>
      <button
        type="button"
        onClick={onAdd}
        disabled={disabled}
        className="flex shrink-0 items-center gap-1 text-xs text-brand-500 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <Plus size={12} /> {addLabel}
      </button>
    </div>
    {children}
  </div>
);

const GroupByRow: React.FC<GroupByRowProps> = ({ group, tables, onChange, onRemove }) => {
  const table = tables.find((t) => t.alias === group.table);
  const { fields } = useSegmentFields(table?.name ?? "");

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={group.table}
        onChange={(e) => onChange({ table: e.target.value, column: "" })}
        className={selectClass}
      >
        {tables.map((t) => (
          <option key={t.alias} value={t.alias}>{t.alias}</option>
        ))}
      </select>

      <select
        value={group.column}
        onChange={(e) => {
          const column = e.target.value;
          onChange({ column, alias: group.alias || column });
        }}
        className={selectClass}
      >
        <option value="">Columna…</option>
        {fields.map((f) => (
          <option key={f.name} value={f.name}>{f.name}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder="alias (opcional)"
        value={group.alias}
        onChange={(e) => onChange({ alias: e.target.value })}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};

const AggregationRow: React.FC<AggregationRowProps> = ({ aggregation, tables, onChange, onRemove }) => {
  const table = tables.find((t) => t.alias === aggregation.table);
  const { fields } = useSegmentFields(table?.name ?? "");
  const isCount = aggregation.function === "count";

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={aggregation.function}
        onChange={(e) => {
          const fn = e.target.value as AggFunction;
          onChange({ function: fn, column: fn === "count" ? "*" : "" });
        }}
        className={selectClass}
      >
        {AGG_FUNCTIONS.map((fn) => (
          <option key={fn.value} value={fn.value}>{fn.label}</option>
        ))}
      </select>

      <select
        value={aggregation.table}
        onChange={(e) => onChange({ table: e.target.value, column: isCount ? "*" : "" })}
        className={selectClass}
      >
        {tables.map((t) => (
          <option key={t.alias} value={t.alias}>{t.alias}</option>
        ))}
      </select>

      <select
        value={aggregation.column}
        onChange={(e) => onChange({ column: e.target.value })}
        disabled={isCount}
        className={`${selectClass} disabled:opacity-60`}
      >
        {isCount && <option value="*">* (todas las filas)</option>}
        {!isCount && <option value="">Columna…</option>}
        {fields.map((f) => (
          <option key={f.name} value={f.name}>{f.name}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder="alias"
        value={aggregation.alias}
        onChange={(e) => onChange({ alias: e.target.value })}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};

const HavingRow: React.FC<HavingRowProps> = ({ having, metricOptions, onChange, onRemove }) => {
  const multiValue = HAVING_OPS_WITH_MULTIPLE_VALUES.includes(having.op);

  return (
    <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
      <select
        value={having.metric}
        onChange={(e) => onChange({ metric: e.target.value })}
        className={selectClass}
      >
        {metricOptions.map((m) => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>

      <select
        value={having.op}
        onChange={(e) => {
          const op = e.target.value as HavingOp;
          onChange({ op, value: HAVING_OPS_WITH_MULTIPLE_VALUES.includes(op) ? [] : "" });
        }}
        className={selectClass}
      >
        {HAVING_OPS.map((op) => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>

      <input
        type="text"
        placeholder={multiValue ? "val1, val2" : "valor"}
        value={
          multiValue
            ? Array.isArray(having.value) ? having.value.join(", ") : ""
            : (having.value as string) ?? ""
        }
        onChange={(e) => {
          const raw = e.target.value;
          onChange({
            value: multiValue ? raw.split(",").map((v) => v.trim()).filter(Boolean) : raw,
          });
        }}
        className={selectClass}
      />

      <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
        <Trash2 size={13} />
      </button>
    </div>
  );
};

const OrderByRow: React.FC<OrderByRowProps> = ({ order, fieldOptions, onChange, onRemove }) => (
  <div className="flex flex-wrap items-center gap-2 xl:flex-nowrap">
    <select
      value={order.field}
      onChange={(e) => onChange({ field: e.target.value })}
      className={selectClass}
    >
      {fieldOptions.map((f) => (
        <option key={f} value={f}>{f}</option>
      ))}
    </select>

    <select
      value={order.direction}
      onChange={(e) => onChange({ direction: e.target.value as SortDirection })}
      className={selectClass}
    >
      <option value="asc">Ascendente</option>
      <option value="desc">Descendente</option>
    </select>

    <button type="button" onClick={onRemove} className="shrink-0 rounded p-1 text-gray-400 hover:text-red-500">
      <Trash2 size={13} />
    </button>
  </div>
);
