import type { ReactNode } from "react";
import { User, UserPlus, Users } from "lucide-react";
import type { RepresentativeMode } from "@/types/companies/company-types";

export const REP_MODES: {
  value: RepresentativeMode;
  label: string;
  icon: ReactNode;
}[] = [
  { value: "self", label: "Yo soy el representante legal", icon: <User size={16} /> },
  { value: "select", label: "Seleccionar usuario existente", icon: <Users size={16} /> },
  { value: "create", label: "Crear nuevo usuario", icon: <UserPlus size={16} /> },
];

export const DOC_TYPE_OPTIONS = [
  { value: "CC", label: "Cédula de ciudadanía (CC)" },
  { value: "CE", label: "Cédula de extranjería (CE)" },
  { value: "NIT", label: "NIT" },
  { value: "PEP", label: "PEP" },
  { value: "PASAPORTE", label: "Pasaporte" },
];
