export interface BillingSummary {
  currentMonthRevenue: string;
  overdueAmount: string;
  billedOrganizationsCount: number;
  collectionRate: number;
}

export interface InvoiceStatusBreakdownItem {
  status: string;
  count: number;
  totalAmount: string;
}

export interface InvoiceStatusBreakdown {
  items: InvoiceStatusBreakdownItem[];
}

export interface RevenueByChannelItem {
  channelName: string;
  totalAmount: string;
}

export interface RevenueByChannel {
  items: RevenueByChannelItem[];
}

export interface RevenueByProviderItem {
  provider: string;
  totalAmount: string;
}

export interface RevenueByProvider {
  items: RevenueByProviderItem[];
}

export interface MonthlyRevenuePoint {
  period: string;
  totalAmount: string;
}

export interface MonthlyRevenue {
  points: MonthlyRevenuePoint[];
}
