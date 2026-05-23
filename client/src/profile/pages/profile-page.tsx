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
    <ModuleBase pageTitle="Perfil" sectionTitle="Mi perfil">
      {loading ? (
        <div className="py-20">
          <Loader />
        </div>
      ) : (
        <div className="space-y-6">
          <ProfileMetaCard
            firstname={profile?.firstname ?? ""}
            lastname={profile?.lastname ?? ""}
            role={profile?.role}
          />
          <ProfileInfoCard
            email={profile?.email ?? ""}
            phone={profile?.phoneNumber}
            nationality={profile?.nationality}
            documentType={profile?.documentType}
            documentNumber={profile?.documentNumber}
          />
        </div>
      )}
    </ModuleBase>
  );
};
