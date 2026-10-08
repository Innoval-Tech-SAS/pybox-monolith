import type { CampaignEditorFormState } from "./campaign-editor-form-state";

export interface StepDetailsProps {
  form: CampaignEditorFormState;
  set: <K extends keyof CampaignEditorFormState>(key: K) => (value: CampaignEditorFormState[K]) => void;
}
