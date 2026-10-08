import { useParams } from "react-router";
import { UserX } from "lucide-react";
import { ModuleBase } from "@/ui/components/common/module-base";
import { UserCard } from "@/profile/components/user-card";
import { useUserDetail } from "../hooks/use-user-detail";
import { Loader } from "@/ui/components/loader/loader";
import EmptyState from "@/ui/components/common/empty-state";

export const UserDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, loading, notFound, canForceLogout, forceLogout } = useUserDetail(id);

  if (loading) {
    return (
      <ModuleBase pageTitle="Usuario" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <div className="flex h-48 items-center justify-center"><Loader loaderText="Cargando usuario..." /></div>
      </ModuleBase>
    );
  }

  if (notFound || !user) {
    return (
      <ModuleBase pageTitle="Usuario no encontrado" breadcrumbItems={[{ label: "Usuarios", path: "/my-users" }]}>
        <EmptyState icon={UserX} title="Usuario no encontrado" className="py-10" />
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
        onForceLogout={canForceLogout ? forceLogout : undefined}
      />
    </ModuleBase>
  );
};
