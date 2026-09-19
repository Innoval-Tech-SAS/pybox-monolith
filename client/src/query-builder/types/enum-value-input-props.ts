import type { FilterOp } from "@/query-builder/types/query-builder-types";

export interface EnumValueInputProps {
  options: string[];
  op: FilterOp;
  value: string | string[] | null;
  onChange: (value: string | string[]) => void;
}
