import type { UserSummary } from "@/types/users/user-types";

export interface UserPickerProps {
  value: string | null;
  onChange: (user: UserSummary | null) => void;
}
