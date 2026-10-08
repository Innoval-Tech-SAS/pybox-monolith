import { useAuth } from "@/hooks/use-auth";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";
import { useUser } from "./use-user";

/**
 * Encapsula la carga del usuario + la acción de forzar cierre de sesión para
 * que user-detail-page.tsx solo orqueste el render.
 */
export const useUserDetail = (userId: string | undefined) => {
  const { user, loading, notFound } = useUser(userId);
  const { getSession } = useAuth();
  const { apiClient } = useApiClient();
  const { success: toastSuccess } = useToast();

  const session = getSession();
  const isGlobal = session?.scope === "GLOBAL";
  const isOrgAdmin = Object.values(session?.orgs ?? {}).some((e) => e.role === "ADMINISTRADOR");
  const canForceLogout = (isGlobal || isOrgAdmin) && !!user && user.id !== session?.userId;

  const forceLogout = async () => {
    if (!user) return;
    await apiClient(`/auth/logout/${user.id}`, { method: "POST" });
    toastSuccess("Sesión cerrada", `Se cerró la sesión de ${user.fullName}.`);
  };

  return { user, loading, notFound, canForceLogout, forceLogout };
};
