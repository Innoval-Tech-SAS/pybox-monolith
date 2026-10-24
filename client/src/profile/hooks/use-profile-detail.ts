import { useCallback } from "react";
import { setSessionUser } from "@/auth/utils/auth-session-utils";
import { useApiClient } from "@/hooks/use-api-client";
import { useAsyncResource } from "@/hooks/use-async-resource";
import type { UserCardData } from "@/profile/types/user-card-props";
import type { User } from "@/types/auth/user";
import type { UserDetail } from "@/types/users/user-types";

/**
 * Encapsula la carga del perfil propio (sesión + detalle) para que
 * profile-page.tsx solo orqueste el render.
 */
export const useProfileDetail = () => {
  const { apiClient } = useApiClient();

  const fetchProfile = useCallback(async (): Promise<UserCardData | null> => {
    const session = (await apiClient("/users/me")) as User;
    const uid = session.userId;
    const detail = uid ? ((await apiClient(`/users/${uid}`)) as UserDetail) : null;

    const data: UserCardData = {
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
      identityVerificationStatus: session.identityVerificationStatus,
      isActiveSessions: detail?.isActiveSessions,
      createdAt: detail?.createdAt,
      updatedAt: detail?.updatedAt,
      orgs: session.orgs,
    };

    if (session) setSessionUser(session);

    return data;
  }, [apiClient]);

  return useAsyncResource<UserCardData | null>(fetchProfile, null);
};
