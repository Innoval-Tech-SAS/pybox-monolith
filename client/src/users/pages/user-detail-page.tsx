import { useParams } from "react-router";
import { ModuleBase } from "@/ui/components/common/module-base";
import { UserCard } from "@/profile/components/user-card";
import { useUser } from "../hooks/use-user";
import { useAuth } from "@/hooks/use-auth";
import { useApiClient } from "@/hooks/use-api-client";
import { useToast } from "@/context/toast-context";

export const UserDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, loading, notFound } = useUser(id);
  const { getSession } = useAuth();
  const { apiClient } = useApiClient();
  const { success: toastSuccess } = useToast();

  const session = getSession();
  const isGlobal = session?.scope === "GLOBAL";
  const isOrgAdmin = Object.values(session?.orgs ?? {}).some((e) => e.role === "ADMINISTRADOR");
  const canForceLogout = (isGlobal || isOrgAdmin) && !!user && user.id !== session?.userId;

  const handleForceLogout = async () => {
    if (!user) return;
    await apiClient(`/auth/logout/${user.id}`, { method: "POST" });
    toastSuccess("Sesión cerrada", `Se cerró la sesión de ${user.fullName}.`);
  };

  if (loading) {
    return (
      <ModuleBase pageTitle="Usuario" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex h-48 items-center justify-center text-gray-400">Cargando...</div>
      </ModuleBase>
    );
  }

  if (notFound || !user) {
    return (
      <ModuleBase pageTitle="Usuario no encontrado" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex h-48 items-center justify-center text-gray-500">Usuario no encontrado.</div>
      </ModuleBase>
    );
  }

  return (
    <ModuleBase
      pageTitle={user.fullName}
      breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}
    >
      <UserCard
        data={{
          userId: user.id,
          fullName: user.fullName,
          firstname: user.firstname,
          lastname: user.lastname,
          email: user.email,
          phoneNumber: user.phoneNumber,
          authProvider: user.authProvider,
          documentType: user.documentType,
          documentNumber: user.documentNumber,
          profilePhotoUrl: user.profilePhotoUrl,
          role: user.roles[0]?.role,
          scope: user.roles[0]?.scope,
          isActive: user.isActive,
          isEmailVerified: user.isEmailVerified,
          isPhoneVerified: user.isPhoneVerified,
          mfaEnabled: user.mfaEnabled,
          isActiveSessions: user.isActiveSessions,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt,
          roles: user.roles,
        }}
        editPath={`/my-users/${user.id}/edit`}
        onForceLogout={canForceLogout ? handleForceLogout : undefined}
      />
    </ModuleBase>
  );
};
