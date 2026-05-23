import type { OnboardingStep } from "@/types/onboarding/onboarding-types";

export const STEP_LABELS: Record<OnboardingStep, string> = {
  email: "Verificar email",
  phone: "Verificar teléfono",
  profile: "Datos del documento",
  organization: "Datos de la empresa",
};

export const STEP_DESCRIPTIONS: Record<OnboardingStep, string> = {
  email: "Confirma que tienes acceso a tu correo electrónico.",
  phone: "Confirma que tienes acceso a tu número de teléfono.",
  profile: "Completa tu información de identificación.",
  organization: "Registra los datos legales de tu empresa.",
};
