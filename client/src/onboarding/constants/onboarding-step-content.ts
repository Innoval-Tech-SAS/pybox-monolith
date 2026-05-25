import type { OnboardingStep } from "@/types/onboarding/onboarding-types";

export const STEP_LABELS: Record<OnboardingStep, string> = {
  set_password: "Crear contraseña",
  email: "Verificar email",
  set_phone: "Registrar teléfono",
  phone: "Verificar teléfono",
  profile: "Datos del documento",
  organization: "Datos de la empresa",
};

export const STEP_DESCRIPTIONS: Record<OnboardingStep, string> = {
  set_password: "Crea una contraseña segura para tu cuenta.",
  email: "Confirma que tienes acceso a tu correo electrónico.",
  set_phone: "Ingresa tu número de teléfono para continuar.",
  phone: "Confirma que tienes acceso a tu número de teléfono.",
  profile: "Completa tu información de identificación.",
  organization: "Registra los datos legales de tu empresa.",
};
