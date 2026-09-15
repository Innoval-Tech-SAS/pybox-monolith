import type { OnboardingRepMode } from "@/types/onboarding/onboarding-types";

export interface RepModeOption {
  value: OnboardingRepMode;
  label: string;
  iconName: "user" | "user-plus";
}

export const REP_MODES: RepModeOption[] = [
  { value: "self", label: "Yo soy el representante legal", iconName: "user" },
  { value: "create", label: "Crear nuevo representante", iconName: "user-plus" },
];

export const WIZARD_STEPS = [
  { title: "Información básica", description: "Nombre y país de tu empresa" },
  { title: "Documentos legales", description: "Sube los registros oficiales" },
  { title: "Representante legal", description: "Quién representa a la empresa" },
] as const;
