import type { BulkSendResponse } from "@/bulk-send/types/bulk-send-types";

export interface ResultCardProps {
  result: BulkSendResponse;
  onReset: () => void;
}
