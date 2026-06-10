import { useState } from "react";
import { Plus, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import { Loader } from "@/ui/components/loader/loader";
import { useSegmentFields } from "@/segments/hooks/use-segment-fields";
import {
  ADDITIONAL_TABLES,
  FILTER_OPS,
  OPS_WITHOUT_VALUE,
  OPS_WITH_MULTIPLE_VALUES,
} from "@/segments/constants/segment.constants";
import type {
  SegmentFormState,
  SegmentFormTable,
  SegmentTableFilter,
  FilterOp,
} from "@/segments/types/segment.types";

interface StepTablesFiltersProps {
  state: SegmentFormState;
  update: (patch: Partial<SegmentFormState>) => void;
  addTable: (table: SegmentFormTable) => void;
  removeTable: (alias: string) => void;
  updateTable: (alias: string, patch: Partial<SegmentFormTable>) => void;
}

export const StepTablesFilters: React.FC<StepTablesFiltersProps> = ({
  state,
  update,
  addTable,
  removeTable,
  updateTable,
}) => {
  const [addingTable, setAddingTable] = useState("");

  const availableToAdd = ADDITIONAL_TABLES.filter(
    (t) =>
      t.name !== state.mainTable &&
      !state.additionalTables.some((a) => a.name === t.name),
  );

  const handleAddTable = () => {
    if (!addingTable) return;
    const meta = ADDITIONAL_TABLES.find((t) => t.name === addingTable);
    if (!meta) return;
    addTable({ name: meta.name, alias: meta.name, columns: [], filters: [] });
    setAddingTable("");
  };

  return (
    <div className="space-y-5">
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

      {/* Add table */}
      {availableToAdd.length > 0 && (
        <div className="flex items-center gap-2">
          <select
            value={addingTable}
            onChange={(e) => setAddingTable(e.target.value)}
            className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 outline-none transition focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
          >
            <option value="">Agregar tabla…</option>
            {availableToAdd.map((t) => (
              <option key={t.name} value={t.name}>
                {t.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={handleAddTable}
            disabled={!addingTable}
            className="flex items-center gap-1.5 rounded-lg bg-brand-500 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-600 disabled:opacity-40"
          >
            <Plus size={15} />
            Agregar
          </button>
        </div>
      )}
    </div>
  );
};

interface TableSectionProps {
  title: string;
  tableName: string;
  columns: string[];
  filters: SegmentTableFilter[];
  onColumnsChange: (cols: string[]) => void;
  onFiltersChange: (filters: SegmentTableFilter[]) => void;
  removable: boolean;
  onRemove?: () => void;
}

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
  const { fields, loading } = useSegmentFields(tableName);
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

  const updateFilter = (i: number, patch: Partial<SegmentTableFilter>) => {
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
                <div className="flex flex-wrap gap-2">
                  {fields.map((f) => (
                    <label
                      key={f.name}
                      className="flex cursor-pointer items-center gap-1.5 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs transition-colors hover:border-brand-300 dark:border-gray-700"
                    >
                      <input
                        type="checkbox"
                        checked={columns.includes(f.name)}
                        onChange={() => toggleColumn(f.name)}
                        className="accent-brand-500"
                      />
                      <span className="text-gray-700 dark:text-gray-300">{f.name}</span>
                      <span className="text-gray-400 dark:text-gray-500">({f.type})</span>
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
                        fields={fields.map((fi) => fi.name)}
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

interface FilterRowProps {
  filter: SegmentTableFilter;
  fields: string[];
  onChange: (patch: Partial<SegmentTableFilter>) => void;
  onRemove: () => void;
}

const FilterRow: React.FC<FilterRowProps> = ({ filter, fields, onChange, onRemove }) => {
  const noValue = OPS_WITHOUT_VALUE.includes(filter.op);
  const multiValue = OPS_WITH_MULTIPLE_VALUES.includes(filter.op);

  const handleOpChange = (op: FilterOp) => {
    const patch: Partial<SegmentTableFilter> = { op };
    if (OPS_WITHOUT_VALUE.includes(op)) patch.value = null;
    else if (OPS_WITH_MULTIPLE_VALUES.includes(op)) patch.value = [];
    else patch.value = "";
    onChange(patch);
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <select
        value={filter.column}
        onChange={(e) => onChange({ column: e.target.value })}
        className="rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
      >
        {fields.map((f) => (
          <option key={f} value={f}>{f}</option>
        ))}
      </select>

      <select
        value={filter.op}
        onChange={(e) => handleOpChange(e.target.value as FilterOp)}
        className="rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
      >
        {FILTER_OPS.map((op) => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>

      {!noValue && (
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
          className="flex-1 min-w-24 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs text-gray-700 outline-none focus:border-brand-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
        />
      )}

      <button
        type="button"
        onClick={onRemove}
        className="rounded p-1 text-gray-400 hover:text-red-500"
      >
        <Trash2 size={13} />
      </button>
    </div>
  );
};
