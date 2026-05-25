import type { UserSummary } from "@/types/users/user-types";

export type SortKey = "fullName" | "email" | "createdAt";
export type SortOrder = "asc" | "desc";

export interface UsersDataTableProps {
  users: UserSummary[];
  loading: boolean;
  onToggleStatus: (userId: number, isActive: boolean) => void;
  onDelete: (userId: number) => void;
}
