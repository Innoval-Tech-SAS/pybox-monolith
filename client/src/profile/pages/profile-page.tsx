import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { User } from "@/types/auth/user";
import { ModuleBase } from "@/ui/components/common/module-base";
import { Loader } from "@/ui/components/loader/loader";
import { ProfileMetaCard } from "../components/profile-meta-card";
import { ProfileInfoCard } from "../components/profile-info-card";

export const ProfilePage: React.FC = () => {
  const { fetchMe } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMe()
      .then((data) => {
        setProfile(data);
        sessionStorage.setItem("user", JSON.stringify(data));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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
