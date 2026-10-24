import type { PeriodicityOption, WeekdayOption } from "@/types/campaigns/campaign-types";
import type { CampaignEditorFormState } from "./campaign-editor-form-state";

export interface StepScheduleProps {
  form: CampaignEditorFormState;
  recurringPeriodicities: PeriodicityOption[];
  weekdays: WeekdayOption[];
  set: <K extends keyof CampaignEditorFormState>(key: K) => (value: CampaignEditorFormState[K]) => void;
}
