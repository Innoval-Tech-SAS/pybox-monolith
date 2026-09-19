export interface OrganizationStats {
  portfoliosCount: number;
  portfoliosActiveCount: number;
  portfoliosInactiveCount: number;
  creditsCount: number;
  debtorsCount: number;
  uniqueDebtorsCount: number;
  totalOverdueAmount: number;
  debtorsLoadedPercentage: number;
}

export interface DashboardCampaignOption {
  id: string;
  name: string;
}

export interface MonthlySendsPoint {
  period: string;
  count: number;
}

export interface MonthlySends {
  campaignId: string;
  campaignName: string;
  points: MonthlySendsPoint[];
}

export interface SendStatusCount {
  status: string;
  count: number;
}

export interface SendStatusCounts {
  items: SendStatusCount[];
}
