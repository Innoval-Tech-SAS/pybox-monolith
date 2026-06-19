import type { Channel } from "@/types/channels/channel-types";
import type { CampaignEditorFormState } from "./campaign-editor-form-state";

export interface StepDetailsProps {
  form: CampaignEditorFormState;
  channels: Channel[];
  set: <K extends keyof CampaignEditorFormState>(key: K) => (value: CampaignEditorFormState[K]) => void;
}
