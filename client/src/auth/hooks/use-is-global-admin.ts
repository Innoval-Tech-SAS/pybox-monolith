import { Role, Scope } from "@/types/auth/role";
import { useSession } from "./use-session";

/** Solo el Admin Global puede ver elementos eliminados y restaurarlos, en cualquier
 * CRUD. Centralizado acá para no repetir la comparación de role+scope en cada página. */
export const useIsGlobalAdmin = (): boolean => {
  const { role, scope } = useSession();
  return role === Role.ADMIN && scope === Scope.GLOBAL;
};
