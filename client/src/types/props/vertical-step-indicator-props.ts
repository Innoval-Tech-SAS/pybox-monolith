import type { WizardStep } from "@/types/props/wizard-form-props";

export interface VerticalStepIndicatorProps {
  steps: readonly WizardStep[];
  current: number;
}
