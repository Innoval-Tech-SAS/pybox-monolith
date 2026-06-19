import type { Campaign } from "@/types/campaigns/campaign-types";
import type { Channel } from "@/types/channels/channel-types";

export interface CampaignsTableProps {
  items: Campaign[];
  channels: Channel[];
  isAdmin: boolean;
  saving: boolean;
  total: number;
  page: number;
  pages: number;
  onActivate: (id: string) => void;
  onPause: (id: string) => void;
  onEdit: (item: Campaign) => void;
  onDelete: (item: Campaign) => void;
  onPageChange: (page: number) => void;
}
