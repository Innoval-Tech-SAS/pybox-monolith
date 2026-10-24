import type { WizardStep } from "@/types/props/wizard-form-props";
import type { SelectOption } from "@/types/props/select-props";

export const CREATE_TABLE_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Ubicación", description: "Esquema y nombre de la tabla" },
  { title: "Columnas", description: "Define las columnas de la tabla" },
  { title: "Resumen", description: "Revisa y confirma la creación" },
] as const;

export const ALTER_TABLE_WIZARD_STEPS: readonly WizardStep[] = [
  { title: "Tabla", description: "Selecciona el esquema y la tabla" },
  { title: "Cambio", description: "Define la acción a realizar" },
  { title: "Resumen", description: "Revisa y confirma el cambio" },
] as const;

export const ALTER_ACTION_OPTIONS: SelectOption[] = [
  { value: "ADD_COLUMN", label: "Agregar columna" },
  { value: "DROP_COLUMN", label: "Eliminar columna" },
  { value: "MODIFY_COLUMN", label: "Modificar columna" },
  { value: "RENAME_COLUMN", label: "Renombrar columna" },
];
