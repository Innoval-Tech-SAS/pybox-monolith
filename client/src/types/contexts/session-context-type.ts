import type { User } from "@/types/auth/user";
import type { Role, Scope } from "@/types/auth/role";

export interface SessionContextType {
  user: User | null;
  role: Role;
  scope: Scope;
  loading: boolean;
  refetch: () => Promise<void>;
}
