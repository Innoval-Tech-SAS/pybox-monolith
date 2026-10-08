import { useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import type {
  EntityFormState,
  FormTable,
  EntityJoin,
  TableFilter,
  EntityAggregation,
  EntityHaving,
  EntityOrderBy,
  EntityResponse,
} from "@/query-builder/types/query-builder-types";

const EMPTY_STATE: EntityFormState = {
  name: "",
  description: "",
  mainTable: "",
  mainTableColumns: [],
  mainTableFilters: [],
  additionalTables: [],
  joins: [],
  aggregateMode: false,
  groupBy: [],
  aggregations: [],
  having: [],
  orderBy: [],
};

const parseExisting = (entity: EntityResponse): EntityFormState => {
  const criteria = entity.config;
  const tables = (criteria.tables ?? []) as Record<string, unknown>[];
  const joins = (criteria.joins ?? []) as Record<string, unknown>[];

  const main = tables[0] ?? {};
  const rest = tables.slice(1);

  return {
    name: entity.name,
    description: entity.description ?? "",
    mainTable: (main.name as string) ?? "",
    mainTableColumns: (main.columns as string[]) ?? [],
    mainTableFilters: ((main.filters as Record<string, unknown>[]) ?? []).map((f) => ({
      column: f.column as string,
      op: f.op as TableFilter["op"],
      value: (f.value as string | string[] | null) ?? null,
    })),
    additionalTables: rest.map((t) => ({
      name: t.name as string,
      alias: (t.alias as string) ?? (t.name as string),
      columns: (t.columns as string[]) ?? [],
      filters: ((t.filters as Record<string, unknown>[]) ?? []).map((f) => ({
        column: f.column as string,
        op: f.op as TableFilter["op"],
        value: (f.value as string | string[] | null) ?? null,
      })),
    })),
    joins: joins.map((j) => ({
      left: j.left as string,
      right: j.right as string,
      leftOn: ((j.left_on ?? j.leftOn) as string) ?? "",
      rightOn: ((j.right_on ?? j.rightOn) as string) ?? "",
      how: (j.how as EntityJoin["how"]) ?? "inner",
    })),
    aggregateMode: (criteria.query_mode as string) === "aggregate",
    groupBy: ((criteria.group_by as Record<string, unknown>[]) ?? []).map((g) => ({
      table: (g.table as string) ?? "",
      column: g.column as string,
      alias: (g.alias as string) ?? (g.column as string),
    })),
    aggregations: ((criteria.aggregations as Record<string, unknown>[]) ?? []).map((a) => ({
      function: a.function as EntityAggregation["function"],
      table: (a.table as string) ?? "",
      column: a.column as string,
      alias: (a.alias as string) ?? "",
    })),
    having: ((criteria.having as Record<string, unknown>[]) ?? []).map((h) => ({
      metric: h.metric as string,
      op: h.op as EntityHaving["op"],
      value: (h.value as string | string[] | null) ?? null,
    })),
    orderBy: ((criteria.order_by as Record<string, unknown>[]) ?? []).map((o) => ({
      field: o.field as string,
      direction: ((o.direction as string) ?? "asc") as EntityOrderBy["direction"],
    })),
  };
};

const buildPayload = (state: EntityFormState, configKey: "filterCriteria" | "reportConfig") => {
  const tables = [
    {
      name: state.mainTable,
      alias: state.mainTable,
      columns: state.mainTableColumns,
      filters: state.mainTableFilters,
    },
    ...state.additionalTables.map((t) => ({
      name: t.name,
      alias: t.alias,
      columns: t.columns,
      filters: t.filters,
    })),
  ];

  return {
    name: state.name,
    description: state.description || undefined,
    [configKey]: {
      tables,
      joins: state.joins.map((j) => ({
        left: j.left,
        right: j.right,
        leftOn: j.leftOn,
        rightOn: j.rightOn,
        how: j.how,
      })),
      queryMode: state.aggregateMode ? "aggregate" : "detail",
      groupBy: state.aggregateMode ? state.groupBy : [],
      aggregations: state.aggregateMode ? state.aggregations : [],
      having: state.aggregateMode ? state.having : [],
      orderBy: state.aggregateMode ? state.orderBy : [],
    },
  };
};

export const useEntityForm = (
  kind: "segments" | "reports",
  configKey: "filterCriteria" | "reportConfig",
  stepsCount: number,
  scopeId: string,
  onSuccess: () => void,
  existing?: EntityResponse,
) => {
  const { apiClient } = useApiClient();
  const paramName = kind === "segments" ? "portfolioId" : "organizationId";
  const [step, setStep] = useState(0);
  const [state, setState] = useState<EntityFormState>(
    existing ? parseExisting(existing) : EMPTY_STATE,
  );
  const [submitting, setSubmitting] = useState(false);

  const update = (patch: Partial<EntityFormState>) =>
    setState((prev) => ({ ...prev, ...patch }));

  const nextStep = () => setStep((s) => Math.min(s + 1, stepsCount - 1));
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  // Additional tables helpers
  const addTable = (table: FormTable) =>
    update({ additionalTables: [...state.additionalTables, table] });

  const removeTable = (alias: string) =>
    update({
      additionalTables: state.additionalTables.filter((t) => t.alias !== alias),
      joins: state.joins.filter((j) => j.left !== alias && j.right !== alias),
    });

  const updateTable = (alias: string, patch: Partial<FormTable>) =>
    update({
      additionalTables: state.additionalTables.map((t) =>
        t.alias === alias ? { ...t, ...patch } : t,
      ),
    });

  // Joins helpers
  const addJoin = (join: EntityJoin) =>
    update({ joins: [...state.joins, join] });

  const removeJoin = (index: number) =>
    update({ joins: state.joins.filter((_, i) => i !== index) });

  const updateJoin = (index: number, patch: Partial<EntityJoin>) =>
    update({
      joins: state.joins.map((j, i) => (i === index ? { ...j, ...patch } : j)),
    });

  const submit = async () => {
    setSubmitting(true);
    try {
      const payload = buildPayload(state, configKey);
      if (existing) {
        await apiClient(`/${kind}/${existing.id}?${paramName}=${scopeId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await apiClient(`/${kind}/?${paramName}=${scopeId}`, {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      onSuccess();
    } catch {
      // apiClient already shows toast on error
    } finally {
      setSubmitting(false);
    }
  };

  const allTableAliases = [
    { alias: state.mainTable, label: state.mainTable },
    ...state.additionalTables.map((t) => ({ alias: t.alias, label: `${t.name} (${t.alias})` })),
  ];

  return {
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
  };
};
