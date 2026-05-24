import type { UserSummary } from "@/types/users/user-types";

export interface UserPickerProps {
  value: number | null;
  onChange: (user: UserSummary | null) => void;
}
