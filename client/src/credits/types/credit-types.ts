export interface PaymentSummary {
  id: number;
  limitPayDate: string;
  paymentDate: string | null;
  paymentAmount: number;
  installmentNumber: number | null;
  principalPayment: number;
  totalInterestAmount: number;
  otherCharges: number;
}

export interface CreditWithPayments {
  id: number;
  creditNumber: string;
  creditType: string;
  disbursedDate: string;
  totalCreditBalance: number;
  overduePrincipalBalance: number;
  daysOverdueAtCutoff: number;
  role: string;
  organizationName: string;
  currencyCode: string;
  payments: PaymentSummary[];
}
