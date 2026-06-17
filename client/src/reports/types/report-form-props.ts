import type { ReportResponse } from "@/reports/types/report.types";

export interface ReportFormProps {
  orgId: string;
  onSuccess: () => void;
  onCancel: () => void;
  existing?: ReportResponse;
}
