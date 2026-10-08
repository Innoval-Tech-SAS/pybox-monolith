import type { SelectOption } from "@/types/props/select-props";

/** Tipos de documento que Wompi acepta para PSE. */
export const PSE_LEGAL_ID_TYPE_OPTIONS: SelectOption[] = [
  { value: "CC", label: "Cédula de ciudadanía" },
  { value: "CE", label: "Cédula de extranjería" },
  { value: "NIT", label: "NIT" },
  { value: "PP", label: "Pasaporte" },
  { value: "TI", label: "Tarjeta de identidad" },
];
