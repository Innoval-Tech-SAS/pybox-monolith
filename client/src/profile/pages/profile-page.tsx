import React, { useEffect, useState } from "react";
import { useApiClient } from "@/hooks/use-api-client";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { UserCard, type UserCardData } from "../components/user-card";
import type { User } from "@/types/auth/user";
import type { UserDetail } from "@/types/users/user-types";

export const ProfilePage: React.FC = () => {
  const { apiClient } = useApiClient();
  const [data, setData] = useState<UserCardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [session, detail] = await Promise.all([
          apiClient("/users/me") as Promise<User>,
          (async () => {
            const s = await apiClient("/users/me") as User;
            const uid = s.userId;
            if (!uid) return null;
            return apiClient(`/users/${uid}`) as Promise<UserDetail>;
          })(),
        ]);

        setData({
          userId: session.userId,
          fullName: session.fullName ?? "",
          firstname: detail?.firstname,
          lastname: detail?.lastname,
          email: session.email,
          phoneNumber: detail?.phoneNumber,
          authProvider: detail?.authProvider,
          documentType: session.documentType ?? detail?.documentType,
          documentNumber: session.documentNumber ?? detail?.documentNumber,
          profilePhotoUrl: session.profilePhotoUrl ?? detail?.profilePhotoUrl,
          role: session.role,
          scope: session.scope,
          isActive: detail?.isActive,
          isEmailVerified: detail?.isEmailVerified,
          isPhoneVerified: detail?.isPhoneVerified,
          mfaEnabled: session.mfaEnabled ?? detail?.mfaEnabled,
          isActiveSessions: detail?.isActiveSessions,
          createdAt: detail?.createdAt,
          updatedAt: detail?.updatedAt,
          orgs: session.orgs,
        });
        if (session) sessionStorage.setItem("user", JSON.stringify(session));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <ModuleBase pageTitle="Perfil">
      {loading || !data ? (
        <div className="py-20"><Loader /></div>
      ) : (
        <UserCard data={data} isOwnProfile />
      )}
    </ModuleBase>
  );
};
