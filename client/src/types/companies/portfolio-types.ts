export interface Portfolio {
  id: string;
  name: string;
  description: string | null;
  organizationId: string;
  country: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string | null;
}
