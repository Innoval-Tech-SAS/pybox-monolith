import type { ReportResponse } from "@/reports/types/report.types";

export interface ReportExecuteModalProps {
  isOpen: boolean;
  onClose: () => void;
  report: ReportResponse;
  orgId: string;
}
