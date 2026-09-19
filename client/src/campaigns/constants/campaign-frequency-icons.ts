import { Zap, CalendarClock, Repeat } from "lucide-react";
import type { CampaignFrequency } from "@/campaigns/types/campaign-editor-form-state";

export const FREQUENCY_ICONS: Record<CampaignFrequency, typeof Zap> = {
  INMEDIATO: Zap,
  UNA_VEZ: CalendarClock,
  PERIODICO: Repeat,
};
