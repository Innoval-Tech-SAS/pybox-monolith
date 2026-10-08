export interface BulkSendResponse {
  total_sent: number;
  success_count: number;
  failure_count: number;
  unique_customers: number;
  skipped_rows: number;
}
