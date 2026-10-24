import type { RepresentativeMode } from "@/types/companies/company-types";

export interface RegisterOrgRepMode {
  value: RepresentativeMode;
  label: string;
  iconName: "user" | "users" | "user-plus";
}

export const REP_MODES: RegisterOrgRepMode[] = [
  { value: "self", label: "Yo soy el representante legal", iconName: "user" },
  {
    value: "select",
    label: "Usuario existente",
    iconName: "users",
  },
  { value: "create", label: "Nuevo usuario", iconName: "user-plus" },
];

export const WIZARD_STEPS = [
  {
    title: "Datos de la empresa",
    description: "Nombre, país y registro fiscal",
  },
  {
    title: "Documentos legales",
    description: "Documentos de constitución",
  },
  {
    title: "Representante legal",
    description: "Quién representa a la empresa",
  },
] as const;
