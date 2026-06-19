import type { UserSummary } from "@/types/users/user-types";

export type SortKey = "fullName" | "createdAt";
export type SortOrder = "asc" | "desc";

export interface UsersDataTableProps {
  users: UserSummary[];
  loading: boolean;
  orgId?: string;
  onToggleStatus: (userId: string, isActive: boolean) => void;
  onDelete: (user: UserSummary) => void;
}
