export interface ReportsTableProps {
  reports: import("@/reports/types/report.types").ReportResponse[];
  loading: boolean;
  onEdit: (report: import("@/reports/types/report.types").ReportResponse) => void;
  onExecute: (report: import("@/reports/types/report.types").ReportResponse) => void;
  onHistory: (report: import("@/reports/types/report.types").ReportResponse) => void;
  onDelete: (report: import("@/reports/types/report.types").ReportResponse) => void;
}

export interface ActionBtnProps {
  title: string;
  onClick: () => void;
  icon: React.ReactNode;
  danger?: boolean;
}
