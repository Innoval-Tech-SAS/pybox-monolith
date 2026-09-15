export type PaymentResultStatus = "APPROVED" | "DECLINED" | "PENDING" | "ERROR";

export interface PaymentResultConfig {
  icon: React.ReactNode;
  title: string;
  message: string;
  color: string;
}
