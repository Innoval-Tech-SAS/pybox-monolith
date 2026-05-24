export interface WizardStep {
  title: string;
  description: string;
}

export interface WizardFormProps {
  steps: readonly WizardStep[];
  canAdvance: (step: number) => boolean;
  canSubmit: boolean;
  onSubmit: (e: React.FormEvent) => void;
  onBack?: () => void;
  loading?: boolean;
  submitLabel?: string;
  loadingLabel?: string;
  children: (step: number) => React.ReactNode;
}
