import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { User } from "@/types/auth/user";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ProfileMetaCard } from "../components/profile-meta-card";
import { ProfileInfoCard } from "../components/profile-info-card";
import { resolveProfilePhotoUrl } from "../utils/profile-photo-url";

export const ProfilePage: React.FC = () => {
  const { fetchMe } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("[profile-photo] profile fetch start");
    fetchMe()
      .then((data) => {
        console.log("[profile-photo] profile fetch response", {
          profile_photo_url: data.profile_photo_url,
          profilePhotoUrl: data.profilePhotoUrl,
          profilePhoto: data.profilePhoto,
          fullName: data.full_name ?? data.fullname,
        });
        setProfile(data);
        sessionStorage.setItem("user", JSON.stringify(data));
      })
      .catch((error) => {
        console.log("[profile-photo] profile fetch error", error);
      })
      .finally(() => {
        console.log("[profile-photo] profile fetch end");
        setLoading(false);
      });
  }, []);

  const rawProfilePhotoUrl = profile?.profile_photo_url ?? profile?.profilePhotoUrl ?? profile?.profilePhoto;
  const avatarUrl = resolveProfilePhotoUrl(rawProfilePhotoUrl);
  console.log("[profile-photo] profile render", {
    loading,
    rawProfilePhotoUrl,
    avatarUrl,
  });

  return (
    <ModuleBase pageTitle="Perfil">
      {loading ? (
        <div className="py-20">
          <Loader />
        </div>
      ) : (
        <div className="space-y-6">
          <ProfileMetaCard
            fullName={profile?.full_name ?? profile?.fullname ?? ""}
            role={profile?.role ?? (profile?.orgs ? Object.values(profile.orgs)[0]?.role : undefined)}
            scope={profile?.scope}
            avatarUrl={avatarUrl}
          />
          <ProfileInfoCard
            email={profile?.email ?? ""}
            documentType={profile?.document_type ?? profile?.documentType}
            documentNumber={profile?.document_number ?? profile?.documentNumber}
            orgs={profile?.orgs}
          />
        </div>
      )}
    </ModuleBase>
  );
};
