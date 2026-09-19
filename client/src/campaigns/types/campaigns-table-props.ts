import type { Campaign } from "@/types/campaigns/campaign-types";
import type { Channel } from "@/types/channels/channel-types";
import type { SortOrder } from "@/ui/components/table/sort-icon";
import type { CampaignSortKey } from "@/campaigns/hooks/use-campaigns";

export interface CampaignsTableProps {
  items: Campaign[];
  channels: Channel[];
  isAdmin: boolean;
  saving: boolean;
  loading: boolean;
  total: number;
  page: number;
  pages: number;
  search: string;
  pageSize: number;
  sortKey: CampaignSortKey;
  sortOrder: SortOrder;
  onSearch: (q: string) => void;
  onPageSizeChange: (size: number) => void;
  onSort: (key: CampaignSortKey) => void;
  onActivate: (id: string) => void;
  onPause: (id: string) => void;
  onEdit: (item: Campaign) => void;
  /** Abre el monitor en vivo. Solo se ofrece en campañas del canal CALL. */
  onMonitor: (item: Campaign) => void;
  /** Abre el reporte de resultados. Solo se ofrece en campañas del canal CALL. */
  onResults: (item: Campaign) => void;
  onDelete: (item: Campaign) => void;
  onPageChange: (page: number) => void;
}
