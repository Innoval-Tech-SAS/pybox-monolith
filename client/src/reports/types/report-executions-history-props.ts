import type { ReportResponse } from "@/reports/types/report.types";

export interface ReportExecutionsHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  report: ReportResponse;
  orgId: string;
}
