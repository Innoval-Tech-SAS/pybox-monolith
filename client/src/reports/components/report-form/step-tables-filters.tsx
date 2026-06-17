import { useState } from "react";
import { Plus, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { Dropdown } from "@/ui/components/dropdown/dropdown";
import { DropdownItem } from "@/ui/components/dropdown/dropdown-item";
import { useReportFields } from "@/reports/hooks/use-report-fields";
import {
  ADDITIONAL_TABLES,
  FILTER_OPS,
  OPS_WITHOUT_VALUE,
  OPS_WITH_MULTIPLE_VALUES,
} from "@/reports/constants/report.constants";
import {
  RELATIVE_VALUE_OPTIONS,
  buildOffsetToken,
  detectRelativeMode,
  isDateLikeType,
  type RelativeMode,
} from "@/reports/utils/relative-date";
import type {
  ReportTableFilter,
  FilterOp,
} from "@/reports/types/report.types";
import type { StepTablesFiltersProps, TableSectionProps, FilterRowProps } from "@/reports/types/step-tables-filters-props";

const TYPE_LABELS: Record<string, string> = {
  "character varying": "texto",
  text: "texto",
  uuid: "uuid",
  integer: "entero",
  bigint: "entero",
  smallint: "entero",
  numeric: "número",
  "double precision": "número",
  boolean: "sí/no",
  date: "fecha",
  "timestamp with time zone": "fecha y hora",
  "timestamp without time zone": "fecha y hora",
  "USER-DEFINED": "categoría",
  jsonb: "json",
  json: "json",
};

const friendlyType = (type: string): string => TYPE_LABELS[type] ?? type;

export const StepTablesFilters: React.FC<StepTablesFiltersProps> = ({
  state,
  update,
  addTable,
  removeTable,
  updateTable,
}) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const availableToAdd = ADDITIONAL_TABLES.filter(
    (t) =>
      t.name !== state.mainTable &&
      !state.additionalTables.some((a) => a.name === t.name),
  );

  const handleAddTable = (name: string) => {
    const meta = ADDITIONAL_TABLES.find((t) => t.name === name);
    if (!meta) return;
    addTable({ name: meta.name, alias: meta.name, columns: [], filters: [] });
    setMenuOpen(false);
  };

  return (
    <div className="space-y-5">
      {availableToAdd.length > 0 && (
        <div className="relative flex justify-end">
          <button
            type="button"
            onClick={() => setMenuOpen((o) => !o)}
            className="dropdown-toggle flex items-center gap-1.5 rounded-lg bg-brand-500 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-600"
          >
            <Plus size={15} />
            Agregar tabla
          </button>
          <Dropdown isOpen={menuOpen} onClose={() => setMenuOpen(false)} className="w-56 py-1.5">
            {availableToAdd.map((t) => (
              <DropdownItem key={t.name} onClick={() => handleAddTable(t.name)}>
                {t.label}
              </DropdownItem>
            ))}
          </Dropdown>
        </div>
      )}

      <div className="grid grid-cols-1 items-start gap-4 xl:grid-cols-2">
        {/* Main table */}
        <TableSection
          title={`${state.mainTable} (tabla principal)`}
          tableName={state.mainTable}
          columns={state.mainTableColumns}
          filters={state.mainTableFilters}
          onColumnsChange={(cols) => update({ mainTableColumns: cols })}
          onFiltersChange={(filters) => update({ mainTableFilters: filters })}
          removable={false}
        />

        {/* Additional tables */}
        {state.additionalTables.map((t) => (
          <TableSection
            key={t.alias}
            title={`${t.name}`}
            tableName={t.name}
            columns={t.columns}
            filters={t.filters}
            onColumnsChange={(cols) => updateTable(t.alias, { columns: cols })}
            onFiltersChange={(filters) => updateTable(t.alias, { filters })}
            removable
            onRemove={() => removeTable(t.alias)}
          />
        ))}
      </div>
    </div>
  );
};

const TableSection: React.FC<TableSectionProps> = ({
  title,
  tableName,
  columns,
  filters,
  onColumnsChange,
  onFiltersChange,
  removable,
  onRemove,
}) => {
  const { fields, loading } = useReportFields(tableName);
  const [collapsed, setCollapsed] = useState(false);

  const toggleColumn = (col: string) => {
    onColumnsChange(
      columns.includes(col) ? columns.filter((c) => c !== col) : [...columns, col],
    );
  };

  const addFilter = () => {
    const firstField = fields[0]?.name ?? "";
    onFiltersChange([...filters, { column: firstField, op: "=", value: "" }]);
  };

  const updateFilter = (i: number, patch: Partial<ReportTableFilter>) => {
    onFiltersChange(filters.map((f, idx) => (idx === i ? { ...f, ...patch } : f)));
  };

  const removeFilter = (i: number) => {
    onFiltersChange(filters.filter((_, idx) => idx !== i));
  };

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700">
      <div
        className="flex cursor-pointer items-center justify-between px-4 py-3"
        onClick={() => setCollapsed((c) => !c)}
      >
        <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">{title}</span>
        <div className="flex items-center gap-2">
          {removable && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onRemove?.(); }}
              className="rounded p-1 text-gray-400 hover:text-red-500"
            >
              <Trash2 size={14} />
            </button>
          )}
          {collapsed ? <ChevronDown size={16} className="text-gray-400" /> : <ChevronUp size={16} className="text-gray-400" />}
        </div>
      </div>

      {!collapsed && (
        <div className="border-t border-gray-100 px-4 pb-4 pt-3 space-y-4 dark:border-gray-700">
          {loading ? (
            <div className="py-4"><Loader /></div>
          ) : (
            <>
              {/* Column selector */}
              <div>
                <p className="mb-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Columnas a incluir
                </p>
                <div className="grid max-h-72 grid-cols-2 gap-2 overflow-y-auto pr-1 custom-scrollbar">
                  {fields.map((f) => (
                    <label
                      key={f.name}
                      title={f.name}
                      className="flex cursor-pointer items-start gap-1.5 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs transition-colors hover:border-brand-300 dark:border-gray-700"
                    >
                      <input
                        type="checkbox"
                        checked={columns.includes(f.name)}
                        onChange={() => toggleColumn(f.name)}
                        className="mt-0.5 accent-brand-500 shrink-0"
                      />
                      <span className="flex min-w-0 flex-col">
                        <span className="break-words text-gray-700 dark:text-gray-300">{f.name}</span>
                        <span className="text-[10px] text-gray-400 dark:text-gray-500">{friendlyType(f.type)}</span>
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Filters */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Filtros
                  </p>
                  <button
                    type="button"
                    onClick={addFilter}
                    className="flex items-center gap-1 text-xs text-brand-500 hover:text-brand-600"
                  >
                    <Plus size={12} /> Agregar filtro
                  </button>
                </div>

                {filters.length === 0 ? (
                  <p className="text-xs text-gray-400 dark:text-gray-500">Sin filtros.</p>
                ) : (
                  <div className="space-y-2">
                    {filters.map((f, i) => (
                      <FilterRow
                        key={i}
                        filter={f}
                        fields={fields}
                        onChange={(patch) => updateFilter(i, patch)}
                        onRemove={() => removeFilter(i)}
                      />
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

const FilterRow: React.FC<FilterRowProps> = ({ filter, fields, onChange, onRemove }) => {
  const noValue = OPS_WITHOUT_VALUE.includes(filter.op);
  const multiValue = OPS_WITH_MULTIPLE_VALUES.includes(filter.op);
  const selectedField = fields.find((f) => f.name === filter.column);
  const isDateField = !!selectedField && isDateLikeType(selectedField.type);
  const { mode, days } = detectRelativeMode(filter.op, filter.value);
  const rangeForced = mode === "this_week" || mode === "this_month";

  const handleOpChange = (op: FilterOp) => {
    const patch: Partial<ReportTableFilter> = { op };
    if (OPS_WITHOUT_VALUE.includes(op)) patch.value = null;
    else if (rangeForced) patch.value = multiValue ? [] : "";
    else if (mode === "now") patch.value = "@now";
    else if (mode === "offset") patch.value = buildOffsetToken(days);
    else if (OPS_WITH_MULTIPLE_VALUES.includes(op)) patch.value = [];
    else patch.value = "";
    onChange(patch);
  };

  const handleModeChange = (next: RelativeMode) => {
    const resetOp = (patch: Partial<ReportTableFilter>) =>
      filter.op === "between" ? { ...patch, op: "=" as FilterOp } : patch;

    if (next === "fixed") return onChange(resetOp({ value: "" }));
    if (next === "now") return onChange(resetOp({ value: "@now" }));
    if (next === "offset") return onChange(resetOp({ value: buildOffsetToken(7) }));
    if (next === "this_week") return onChange({ op: "between", value: ["@week_start", "@week_end"] });
    return onChange({ op: "between", value: ["@month_start", "@month_end"] });
  };

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,2fr)_auto] sm:items-center">
      <select
        value={filter.column}
        onChange={(e) => onChange({ column: e.target.value })}
        className="w-full rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
      >
        {fields.map((f) => (
          <option key={f.name} value={f.name}>{f.name}</option>
        ))}
      </select>

      <select
        value={filter.op}
        onChange={(e) => handleOpChange(e.target.value as FilterOp)}
        disabled={rangeForced}
        className="w-full rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 disabled:opacity-60 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
      >
        {FILTER_OPS.map((op) => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>

      {noValue ? (
        <div className="col-span-2 sm:col-span-1" />
      ) : isDateField ? (
        <div className="col-span-2 flex items-center gap-2 sm:col-span-1">
          <select
            value={mode}
            onChange={(e) => handleModeChange(e.target.value as RelativeMode)}
            className="w-32 shrink-0 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
          >
            {RELATIVE_VALUE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          {mode === "fixed" && (
            <input
              type="text"
              placeholder={multiValue ? "val1, val2" : "valor"}
              value={
                multiValue
                  ? Array.isArray(filter.value) ? filter.value.join(", ") : ""
                  : (filter.value as string) ?? ""
              }
              onChange={(e) => {
                const raw = e.target.value;
                onChange({
                  value: multiValue
                    ? raw.split(",").map((v) => v.trim()).filter(Boolean)
                    : raw,
                });
              }}
              className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
            />
          )}

          {mode === "offset" && (
            <input
              type="number"
              value={days}
              onChange={(e) => onChange({ value: buildOffsetToken(Number(e.target.value) || 0) })}
              placeholder="± días"
              className="w-20 min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
            />
          )}

          {(mode === "now" || rangeForced) && (
            <span className="flex-1 truncate text-xs italic text-gray-400 dark:text-gray-500">
              se calcula al ejecutar
            </span>
          )}
        </div>
      ) : (
        <input
          type="text"
          placeholder={multiValue ? "val1, val2, val3" : "valor"}
          value={
            multiValue
              ? Array.isArray(filter.value) ? filter.value.join(", ") : ""
              : (filter.value as string) ?? ""
          }
          onChange={(e) => {
            const raw = e.target.value;
            onChange({
              value: multiValue
                ? raw.split(",").map((v) => v.trim()).filter(Boolean)
                : raw,
            });
          }}
          className="col-span-2 w-full rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300 sm:col-span-1"
        />
      )}

      <button
        type="button"
        onClick={onRemove}
        className="justify-self-end rounded p-1 text-gray-400 hover:text-red-500 sm:justify-self-start"
      >
        <Trash2 size={13} />
      </button>
    </div>
  );
};
