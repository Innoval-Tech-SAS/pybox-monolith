import { ENUM_UNSUPPORTED_OPS, FILTER_OPS } from "@/query-builder/constants/query-builder-constants";
import type { FieldInfo, FilterOp } from "@/query-builder/types/query-builder-types";

export const isEnumField = (field: FieldInfo | undefined): field is FieldInfo & { enumValues: string[] } =>
  !!field?.enumValues && field.enumValues.length > 0;

export const getFilterOpsForField = (field: FieldInfo | undefined): { value: FilterOp; label: string }[] =>
  isEnumField(field) ? FILTER_OPS.filter((op) => !ENUM_UNSUPPORTED_OPS.includes(op.value)) : FILTER_OPS;
